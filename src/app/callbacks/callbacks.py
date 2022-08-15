import yaml

import dash
from dash.dependencies import Input, Output, State
from flask import send_file

from src.app.callbacks.init import figsDefault
from src.app.app import dash_app
from src.app.callbacks.update import updateScenarioInputSimple, updateScenarioInputAdvanced
from src.config_load_app import figNames, figs_cfg, subfigsDisplayed, app_cfg
from src.data.data import getFullData
from src.config_load import input_data, plots
from src.filepaths import getFilePathAssets, getFilePath
from src.plotting.styling.webapp import addWebappSpecificStyling
from src.plotting.plot_all import plotAllFigs


# general callback for (re-)generating plots
@dash_app.callback(
    [*(Output(subfigName, 'figure') for subfigName in subfigsDisplayed),],
    [Input('simple-update', 'n_clicks'),
     Input('advanced-update', 'n_clicks'),
     State('plots-cfg', 'data'),
     State('simple-gwp', 'value'),
     State('simple-important-params', 'data'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),
     State('advanced-params', 'data'),])
def callbackUpdate(n1, n2, plots_cfg: dict,
                   simple_gwp: str, simple_important_params: list,
                   advanced_gwp: str, advanced_times: list, advanced_fuels: list, advanced_params: list):
    ctx = dash.callback_context
    if not ctx.triggered:
        print("Loading figures from default values")
        return *figsDefault.values(),
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-update':
            inputDataUpdated = updateScenarioInputSimple(input_data.copy(), simple_gwp, simple_important_params)
            outputData = getFullData(inputDataUpdated)
            route = '/'
        elif btnPressed == 'advanced-update':
            inputDataUpdated = updateScenarioInputAdvanced(input_data.copy(), advanced_gwp, advanced_times, advanced_fuels, advanced_params)
            outputData = getFullData(inputDataUpdated)
            route = '/advanced'
        else:
            raise Exception('Unknown button pressed!')

    figsNeeded = [fig for fig, routes in app_cfg['figures'].items() if route in routes]
    figs = plotAllFigs(outputData, inputDataUpdated, plots_cfg, global_cfg='webapp', figs_needed=figsNeeded)

    addWebappSpecificStyling(figs)

    return *figs.values(),


# callback for YAML config download
@dash_app.callback(
    Output('download-config-yaml', 'data'),
    [Input('advanced-download-config', 'n_clicks'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),
     State('advanced-params', 'data'),],
     prevent_initial_call=True,)
def callbackDownloadConfig(n, *args):
    scenarioInputUpdated = updateScenarioInputAdvanced(input_data.copy(), *args)
    return dict(content=yaml.dump(scenarioInputUpdated, sort_keys=False), filename='scenario.yml')


# this callback sets the background colour of the rows in the fue table in the advanced tab
@dash_app.callback(
   Output(component_id='advanced-fuels', component_property='style_data_conditional'),
   [Input(component_id='advanced-fuels', component_property='data')])
def callbackTableColour(data: list):
    defaultCondStyle = [
        {'if': {'state': 'active'},
         'backgroundColor': '#80d4ff'},
        {'if': {'state': 'selected'},
         'backgroundColor': '#80d4ff'},
        {'if': {'row_index': 'odd'},
         'backgroundColor': '#FFFFFF'},
        {'if': {'row_index': 'even'},
         'backgroundColor': '#DDDDDD'}
    ]

    for i, row in enumerate(data):
        defaultCondStyle.append({'if': {'row_index': i}, 'backgroundColor': row['colour']})

    return defaultCondStyle


# update parameter values in advanced tab
@dash_app.callback(
    [Output('advanced-modal', 'is_open'),
     Output('advanced-modal-textfield', 'value'),
     Output('advanced-params', 'data'),],
    [Input('advanced-modal-ok', 'n_clicks'),
     Input('advanced-modal-cancel', 'n_clicks'),
     Input('advanced-params', 'active_cell')],
    [State('advanced-modal-textfield', 'value'),
     State('advanced-params', 'data'),],
)
def callbackAdvancedModal(n_ok: int, n_cancel: int, active_cell: int, advanced_modal_textfield: str, data: list):
    ctx = dash.callback_context

    if not ctx.triggered or active_cell['column_id']!='value':
        return False, '', data
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        row = active_cell['row']
        if btnPressed == 'advanced-params':
            return True, str(data[row]['value']), data
        elif btnPressed == 'advanced-modal-cancel':
            return False, '', data
        elif btnPressed == 'advanced-modal-ok':
            data[row]['value'] = advanced_modal_textfield
            return False, '', data
        else:
            raise Exception('Unknown button pressed!')


# update figure plotting settings
settingsButtons = [plotName for plotName, figList in plots.items() if any(f in app_cfg['figures'] and not ('nosettings' in figs_cfg[f] and figs_cfg[f]['nosettings']) for f in figList)]
@dash_app.callback(
    [Output('plot-config-modal', 'is_open'),
     Output('plots-cfg', 'data'),
     Output('plot-config-modal-textfield', 'value'),],
    [*(Input(f'{plotName}-settings', 'n_clicks') for plotName in settingsButtons),
     Input('plot-config-modal-ok', 'n_clicks'),
     Input('plot-config-modal-cancel', 'n_clicks'),],
    [State('plot-config-modal-textfield', 'value'),
     State('plots-cfg', 'data'),],
)
def callbackSettingsModal(*args):
    settings_modal_textfield = args[-2]
    plots_cfg = args[-1]

    ctx = dash.callback_context
    if not ctx.triggered:
        plots_cfg['last_btn_pressed'] = None
        return False, plots_cfg, ''
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed in [f"{cfgName}-settings" for cfgName in plots_cfg]:
            fname = btnPressed.split('-')[0]
            plots_cfg['last_btn_pressed'] = fname
            return True, plots_cfg, plots_cfg[fname]
        elif btnPressed == 'plot-config-modal-cancel':
            return False, plots_cfg, ''
        elif btnPressed == 'plot-config-modal-ok':
            fname = plots_cfg['last_btn_pressed']
            plots_cfg[fname] = settings_modal_textfield
            return False, plots_cfg, ''
        else:
            raise Exception('Unknown button pressed!')


# display of simple or advanced controls
@dash_app.callback(
    Output('simple-controls-card', 'style'),
    Output('advanced-controls-card-left', 'style'),
    Output('advanced-controls-card-right', 'style'),
    *(Output(f"card-{f}", 'style') for f in figNames if f in app_cfg['figures']),
    *(Output(f'{plotName}-settings-div', 'style') for plotName, figList in plots.items() if any(f in app_cfg['figures'] and not ('nosettings' in figs_cfg[f] and figs_cfg[f]['nosettings']) for f in figList)),
    [Input('url', 'pathname')]
)
def callbackDisplayForRoutes(route):
    r = []

    # display of control cards
    r.append({'display': 'none'} if route != '/' else {})
    r.append({'display': 'none'} if route != '/advanced' else {})
    r.append({'display': 'none'} if route != '/advanced' else {})

    # display of figures for different routes
    for figName in figNames:
        if figName not in app_cfg['figures']: continue
        r.append({'display': 'none'} if route not in app_cfg['figures'][figName] else {})

    # display plot config buttons only on advanced
    for figName in figNames:
        if figName not in app_cfg['figures'] or  ('nosettings' in figs_cfg[figName] and figs_cfg[figName]['nosettings']): continue
        r.append({'display': 'none'} if route != '/advanced' else {})

    return r


# path for downloading XLS data file
@dash_app.server.route('/download/data.xlsx')
def callbackDownloadExportdata():
    return send_file(getFilePath('output/', 'data.xlsx'), as_attachment=True)


# serving asset files
@dash_app.server.route('/assets/<path>')
def callbackServeAssets(path):
    return send_file(getFilePathAssets(path), as_attachment=True)
