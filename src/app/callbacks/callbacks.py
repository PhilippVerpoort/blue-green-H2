import pandas as pd
import yaml

import dash
from dash.dependencies import Input, Output, State
from flask import send_file

from src.app.app import dash_app
from src.app.callbacks.update import updateScenarioInputSimple, updateScenarioInputAdvanced
from src.config_load_app import figNames, figs_cfg, allSubFigNames
from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.data.data import getFullData
from src.config_load import input_data, steel_data, plots
from src.filepaths import getFilePathAssets, getFilePath
from src.plotting.export_file import updateFontSizeWebapp
from src.plotting.plot_all import plotAllFigs


# general callback for (re-)generating plots
@dash_app.callback(
    [*(Output(subFigName, 'figure') for subFigName in allSubFigNames),
     Output('table-results', 'data'),
     Output('saved-plot-data', 'data')],
    [Input('simple-update', 'n_clicks'),
     Input('advanced-update', 'n_clicks'),
     Input('results-replot', 'n_clicks'),
     State('table-results', 'data'),
     State('saved-plot-data', 'data'),
     State('plotting-config', 'data'),
     State('simple-gwp', 'value'),
     State('simple-important-params', 'data'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),
     State('advanced-params', 'data'),])
def callbackUpdate(n1, n2, n3, table_results_data: list, saved_plot_data, plotting_cfg: dict,
                   simple_gwp: str, simple_important_params: list,
                   advanced_gwp: str, advanced_times: list, advanced_fuels: list, advanced_params: list):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_data_updated = input_data.copy()
        fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel = getFullData(input_data_updated, steel_data)
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-update':
            input_data_updated = updateScenarioInputSimple(input_data.copy(), simple_gwp, simple_important_params)
            fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel = getFullData(input_data_updated, steel_data)
        elif btnPressed == 'advanced-update':
            input_data_updated = updateScenarioInputAdvanced(input_data.copy(), advanced_gwp, advanced_times, advanced_fuels, advanced_params)
            fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel = getFullData(input_data_updated, steel_data)
        elif btnPressed == 'results-replot':
            # load fuelSpecs and fullParams from session
            fuelSpecs = saved_plot_data['fuelSpecs']
            fullParams = pd.DataFrame(saved_plot_data['fullParams'])
            # convert relevant columns in fullParams Dataframe to int or float
            fullParams['year'] = fullParams['year'].astype(int)
            fullParams['value'] = fullParams['value'].astype(float)
            # load fuel data from table
            fuelData = pd.DataFrame(table_results_data)
            # convert relevant columns in fuelData DataFrame to int or float
            fuelData['year'] = fuelData['year'].astype(int)
            for col in ['cost', 'cost_u', 'ghgi', 'ghgi_u']:
                fuelData[col] = fuelData[col].astype(float)
            # recompute FSCPs
            FSCPData = calcFSCPs(fuelData)
            # TODO: Make sure input_data_updated is initialised! Needs work & testing.
        else:
            raise Exception("Unknown button pressed!")

    figs = plotAllFigs(fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel,
                       input_data, plotting_cfg, global_cfg='webapp')

    updateFontSizeWebapp(figs)

    saved_plot_data = {'fuelSpecs': fuelSpecs, 'fullParams': fullParams.to_dict()}

    return *figs.values(), fuelData.to_dict('records'), saved_plot_data


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
    return dict(content=yaml.dump(scenarioInputUpdated, sort_keys=False), filename="scenario.yml")


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
        return False, "", data
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        row = active_cell['row']
        if btnPressed == 'advanced-params':
            return True, str(data[row]['value']), data
        elif btnPressed == 'advanced-modal-cancel':
            return False, "", data
        elif btnPressed == 'advanced-modal-ok':
            data[row]['value'] = advanced_modal_textfield
            return False, "", data
        else:
            raise Exception("Unknown button pressed!")


# update figure plotting settings
@dash_app.callback(
    [Output('plot-config-modal', 'is_open'),
     Output('plotting-config', 'data'),
     Output('plot-config-modal-textfield', 'value'),],
    [*(Input(f'{plotName}-settings', 'n_clicks') for plotName in plots),
     Input('plot-config-modal-ok', 'n_clicks'),
     Input('plot-config-modal-cancel', 'n_clicks'),],
    [State('plot-config-modal-textfield', 'value'),
     State('plotting-config', 'data'),],
)
def callbackSettingsModal(n1: int, n2: int, n3: int, n4: int, n5: int, n6: int, n_ok: int, n_cancel: int,
                          settings_modal_textfield: str, plotting_cfg: dict):
    ctx = dash.callback_context
    if not ctx.triggered:
        plotting_cfg['last_btn_pressed'] = None
        return False, plotting_cfg, ""
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed in [f"{cfgName}-settings" for cfgName in plotting_cfg]:
            fname = btnPressed.split("-")[0]
            plotting_cfg['last_btn_pressed'] = fname
            return True, plotting_cfg, plotting_cfg[fname]
        elif btnPressed == 'plot-config-modal-cancel':
            return False, plotting_cfg, ""
        elif btnPressed == 'plot-config-modal-ok':
            fname = plotting_cfg['last_btn_pressed']
            plotting_cfg[fname] = settings_modal_textfield
            return False, plotting_cfg, ""
        else:
            raise Exception("Unknown button pressed!")


# display of simple or advanced controls
@dash_app.callback(
    Output('simple-controls-card', 'style'),
    Output('advanced-controls-card-left', 'style'),
    Output('advanced-controls-card-right', 'style'),
    Output('results-card', 'style'),
    *(Output(f"card-{figName}", 'style') for figName in figNames),
    *(Output(f"{plotName}-settings-div", 'style') for plotName in plots),
    [Input('url', 'pathname')]
)
def callbackDisplayForRoutes(route):
    r = []

    r.append({'display': 'none'} if route != '/' else {})
    r.append({'display': 'none'} if route != '/advanced' else {})
    r.append({'display': 'none'} if route != '/advanced' else {})
    r.append({'display': 'none'} if route != '/advanced' else {})

    for figName in figNames:
        r.append({'display': 'none'} if route not in figs_cfg[figName]['display'] else {})

    for figName in figNames:
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
