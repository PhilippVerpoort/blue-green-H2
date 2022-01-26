import pandas as pd
import yaml

import dash
from dash.dependencies import Input, Output, State
from flask import send_file

from src.app.app import app
from src.app.callbacks.update import updateScenarioInputSimple, updateScenarioInputAdvanced
from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.data.data import getFullData
from src.config_load import input_data
from src.filepaths import getFilePathAssets, getFilePath
from src.plotting.loadcfg import n_figs
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6
from src.plotting.plotFig7 import plotFig7


# update figure plotting settings
@app.callback(
    [Output("settings-modal", "is_open"),
     Output("plotting-config", "data"),
     Output("settings-modal-textfield", "value"),],
    [Input("fig1-settings", "n_clicks"),
     Input("fig2-settings", "n_clicks"),
     Input("fig3-settings", "n_clicks"),
     Input("fig4-settings", "n_clicks"),
     Input("fig5-settings", "n_clicks"),
     Input("fig6-settings", "n_clicks"),
     Input("fig7-settings", "n_clicks"),
     Input("settings-modal-ok", "n_clicks"),
     Input("settings-modal-cancel", "n_clicks"),],
    [State("settings-modal-textfield", "value"),
     State("plotting-config", "data"),],
)
def callbackSettingsModal(n1: int, n2: int, n3: int, n4: int, n5: int, n6: int, n7: int, n_ok: int, n_cancel: int,
                          settings_modal_textfield: str, plotting_cfg: dict):
    ctx = dash.callback_context
    if not ctx.triggered:
        plotting_cfg['last_btn_pressed'] = None
        return False, plotting_cfg, ""
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed in [f"fig{f}-settings" for f in range(1, n_figs+1)]:
            fname = btnPressed.split("-")[0]
            plotting_cfg['last_btn_pressed'] = fname
            return True, plotting_cfg, plotting_cfg[fname]
        elif btnPressed == 'settings-modal-cancel':
            return False, plotting_cfg, ""
        elif btnPressed == 'settings-modal-ok':
            fname = plotting_cfg['last_btn_pressed']
            plotting_cfg[fname] = settings_modal_textfield
            return False, plotting_cfg, ""
        else:
            raise Exception("Unknown button pressed!")


# general callback for (re-)generating plots
@app.callback(
    [Output('fig1', 'figure'),
     Output('fig2', 'figure'),
     Output('fig3', 'figure'),
     Output('fig4', 'figure'),
     Output('fig5', 'figure'),
     Output('fig6', 'figure'),
     Output('fig7', 'figure'),
     Output('table-results', 'data'),
     Output('saved-plot-data', 'data')],
    [Input('simple-update', 'n_clicks'),
     Input('advanced-update', 'n_clicks'),
     Input('results-replot', 'n_clicks'),
     State('table-results', 'data'),
     State('saved-plot-data', 'data'),
     State("plotting-config", "data"),
     State('simple-gwp', 'value'),
     State('simple-leakage', 'value'),
     State('simple-ng-price', 'value'),
     State('simple-lifetime', 'value'),
     State('simple-irate', 'value'),
     State('simple-cost-green-capex-2025', 'value'),
     State('simple-cost-green-capex-2050', 'value'),
     State('simple-cost-green-elec-2025', 'value'),
     State('simple-cost-green-elec-2050', 'value'),
     State('simple-ghgi-green-elec', 'value'),
     State('simple-green-ocf', 'value'),
     State('simple-cost-blue-capex-heb', 'value'),
     State('simple-cost-blue-capex-leb', 'value'),
     State('simple-cost-blue-cts-2025', 'value'),
     State('simple-cost-blue-cts-2050', 'value'),
     State('simple-blue-eff-heb', 'value'),
     State('simple-blue-eff-leb', 'value'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),
     State('advanced-params', 'data'),])
def callbackUpdate(n1, n2, n3, table_results_data: list, saved_plot_data, plotting_cfg: dict, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_data_updated = input_data.copy()
        fuelSpecs, fuelData, FSCPData, fullParams = getFullData(input_data_updated)
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-update':
            input_data_updated = updateScenarioInputSimple(input_data.copy(), *args)
            fuelSpecs, fuelData, FSCPData, fullParams = getFullData(input_data_updated)
        elif btnPressed == 'advanced-update':
            input_data_updated = updateScenarioInputAdvanced(input_data.copy(), *args)
            fuelSpecs, fuelData, FSCPData, fullParams = getFullData(input_data_updated)
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

    saved_plot_data = {'fuelSpecs': fuelSpecs, 'fullParams': fullParams.to_dict()}

    fig1 = plotFig1(fuelSpecs, fuelData, FSCPData, yaml.load(plotting_cfg['fig1'], Loader=yaml.FullLoader), export_img=False)
    fig2 = plotFig2(fuelSpecs, fuelData, yaml.load(plotting_cfg['fig2'], Loader=yaml.FullLoader), export_img=False)
    fig3 = plotFig3(fuelSpecs, FSCPData, yaml.load(plotting_cfg['fig3'], Loader=yaml.FullLoader), export_img=False)
    fig4 = plotFig4(fuelSpecs, fuelData, yaml.load(plotting_cfg['fig4'], Loader=yaml.FullLoader), export_img=False)
    fig5 = plotFig5(fuelSpecs, fuelData, fullParams, input_data_updated['fuels'], yaml.load(plotting_cfg['fig5'], Loader=yaml.FullLoader), export_img=False)
    fig6 = plotFig6(fullParams, input_data_updated['fuels'], yaml.load(plotting_cfg['fig6'], Loader=yaml.FullLoader), export_img=False)
    fig7 = plotFig7(fuelSpecs, input_data_updated, fullParams, yaml.load(plotting_cfg['fig7'], Loader=yaml.FullLoader), export_img=False)

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7,\
           fuelData.to_dict('records'), saved_plot_data


# callback for YAML config download
@app.callback(
    Output("download-config-yaml", "data"),
    [Input('simple-download-config', 'n_clicks'),
     Input('advanced-download-config', 'n_clicks'),
     State('simple-gwp', 'value'),
     State('simple-leakage', 'value'),
     State('simple-ng-price', 'value'),
     State('simple-lifetime', 'value'),
     State('simple-irate', 'value'),
     State('simple-cost-green-capex-2025', 'value'),
     State('simple-cost-green-capex-2050', 'value'),
     State('simple-cost-green-elec-2025', 'value'),
     State('simple-cost-green-elec-2050', 'value'),
     State('simple-ghgi-green-elec', 'value'),
     State('simple-green-ocf', 'value'),
     State('simple-cost-blue-capex-heb', 'value'),
     State('simple-cost-blue-capex-leb', 'value'),
     State('simple-cost-blue-cts-2025', 'value'),
     State('simple-cost-blue-cts-2050', 'value'),
     State('simple-blue-eff-heb', 'value'),
     State('simple-blue-eff-leb', 'value'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),
     State('advanced-params', 'data'),],
     prevent_initial_call=True,)
def callbackDownloadConfig(n1, n2, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise Exception("Initial call not prevented!")
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-download-config':
            scenarioInputUpdated = updateScenarioInputSimple(input_data.copy(), *args)
        elif btnPressed == 'advanced-download-config':
            scenarioInputUpdated = updateScenarioInputAdvanced(input_data.copy(), *args)
        else:
            raise Exception("Unknown button pressed!")

    return dict(content=yaml.dump(scenarioInputUpdated, sort_keys=False), filename="scenario.yml")


# this callback sets the background colour of the rows in the fue table in the advanced tab
@app.callback(
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
@app.callback(
    [Output("advanced-modal", "is_open"),
     Output("advanced-modal-textfield", "value"),
     Output("advanced-params", "data"),],
    [Input("advanced-modal-ok", "n_clicks"),
     Input("advanced-modal-cancel", "n_clicks"),
     Input("advanced-params", "active_cell")],
    [State("advanced-modal-textfield", "value"),
     State("advanced-params", "data"),],
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


# path for downloading XLS data file
@app.server.route('/download/data.xlsx')
def callbackDownloadExportdata():
    return send_file(getFilePath('output/', 'data.xlsx'), as_attachment=True)


# serving asset files
@app.server.route('/assets/<path>')
def callbackServeAssets(path):
    return send_file(getFilePathAssets(path), as_attachment=True)
