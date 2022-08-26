import yaml

import dash
from dash.dependencies import Input, Output, State
from flask import send_file

from src.app.callbacks.init import figsDefault
from src.app.app import dash_app
from src.app.callbacks.simple_params import editTablesModal
from src.app.callbacks.update import updateScenarioInput
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
     State('url', 'pathname'),
     State('plots-cfg', 'data'),
     State('simple-gwp', 'value'),
     State('simple-important-params', 'data'),
     State('simple-gas-prices', 'data'),
     State('advanced-params', 'data'),])
def callbackUpdate(n1, route, plots_cfg: dict, simple_gwp: str, simple_important_params: list, simple_gas_prices: list, advanced_params: list):
    ctx = dash.callback_context

    if not ctx.triggered:
        print("Loading figures from default values")
        return *figsDefault.values(),
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-update':
            inputDataUpdated = updateScenarioInput(input_data.copy(), simple_gwp, simple_important_params, simple_gas_prices, advanced_params)
            outputData = getFullData(inputDataUpdated)
        else:
            raise Exception(f"Unknown button pressed: {btnPressed}")

    figsNeeded = [fig for fig, routes in app_cfg['figures'].items() if route in routes]
    figs = plotAllFigs(outputData, inputDataUpdated, plots_cfg, global_cfg='webapp', figs_needed=figsNeeded)

    addWebappSpecificStyling(figs)

    return *figs.values(),


# callback for YAML config download
@dash_app.callback(
    Output('download-config-yaml', 'data'),
    [Input('download-config', 'n_clicks'),
     State('simple-gwp', 'value'),
     State('simple-important-params', 'data'),
     State('simple-gas-prices', 'data'),
     State('advanced-params', 'data'),],
     prevent_initial_call=True,)
def callbackDownloadConfig(n, *args):
    scenarioInputUpdated = updateScenarioInputAdvanced(input_data.copy(), *args)
    return dict(content=yaml.dump(scenarioInputUpdated, sort_keys=False), filename='scenario.yml')


# update parameter values in advanced tab
@dash_app.callback(
    [*(Output(t, 'data') for t in editTablesModal),
     Output('advanced-modal', 'is_open'),
     Output('table-modal-open', 'data'),
     Output('advanced-modal-textfield', 'value'),],
    [*(Input(t, 'active_cell') for t in editTablesModal),
     Input('advanced-modal-ok', 'n_clicks'),
     Input('advanced-modal-cancel', 'n_clicks'),],
    [*(State(t, 'data') for t in editTablesModal),
     State('advanced-modal-textfield', 'value'),
     State('table-modal-open', 'data'),],
)
def callbackAdvancedModal(*args):
    active_cell = {p: args[i] for i, p in enumerate(list(editTablesModal.keys()))}
    current_data = {p: args[i - len(editTablesModal) - 2] for i, p in enumerate(list(editTablesModal.keys()))}
    text_field_data = args[-2]
    origin_saved = args[-1]

    ctx = dash.callback_context

    if not ctx.triggered:
        return *current_data.values(), False, '', ''
    else:
        origin = ctx.triggered[0]['prop_id'].split('.')[0]

        if origin in editTablesModal:
            row = active_cell[origin]['row']
            col = active_cell[origin]['column_id']

            if col not in editTablesModal[origin]:
                return *current_data.values(), False, '', ''
            else:
                return *current_data.values(), True, origin, str(current_data[origin][row][col])
        elif origin == 'advanced-modal-cancel':
            return *current_data.values(), False, '', ''
        elif origin == 'advanced-modal-ok':
            row = active_cell[origin_saved]['row']
            col = active_cell[origin_saved]['column_id']

            current_data[origin_saved][row][col] = text_field_data
            return *current_data.values(), False, '', ''
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
    Output('advanced-controls-card-right', 'style'),
    *(Output(f"card-{f}", 'style') for f in figNames if f in app_cfg['figures']),
    *(Output(f'{plotName}-settings-div', 'style') for plotName, figList in plots.items() if any(f in app_cfg['figures'] and not ('nosettings' in figs_cfg[f] and figs_cfg[f]['nosettings']) for f in figList)),
    [Input('url', 'pathname')]
)
def callbackDisplayForRoutes(route):
    r = []

    # display of control cards
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
