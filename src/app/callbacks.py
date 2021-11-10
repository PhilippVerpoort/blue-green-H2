import pandas as pd
import yaml

import dash
from dash.dependencies import Input, Output, State
from flask import send_file

from server import app, scenarioInputDefault
from src.app.update import updateScenarioInputSimple, updateScenarioInputAdvanced
from src.data.calc_FSCPs import calcFSCPs
from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6


# update figure plotting settings
@app.callback(
    [Output("settings-modal", "is_open"),
     Output("plotting-config", "data"),
     Output("settings-modal-textfield", "value"),],
    [Input("fig1-settings", "n_clicks"),
     Input("settings-modal-ok", "n_clicks"),
     Input("settings-modal-cancel", "n_clicks"),],
    [State("settings-modal", "is_open"),
     State("settings-modal-textfield", "value"),
     State("plotting-config", "data"),],
)
def callbackSettingsModal(n1: int, n_ok: int, n_cancel: int, is_open: bool, settings_modal_textfield: str, plotting_cfg: dict):
    ctx = dash.callback_context
    if not ctx.triggered:
        plotting_cfg = {
            'fig1': yaml.load(open('input/plotting/config_fig1.yml', 'r').read(), Loader=yaml.FullLoader)
        }
        return False, plotting_cfg, ""
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed in ['fig1-settings']:
            return True, plotting_cfg, yaml.dump(plotting_cfg['fig1'], sort_keys=False)
        elif btnPressed == 'settings-modal-cancel':
            return False, plotting_cfg, ""
        elif btnPressed == 'settings-modal-ok':
            plotting_cfg['fig1'] = yaml.load(settings_modal_textfield, Loader=yaml.FullLoader)
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
     Output('table-results', 'data'),
     Output('fuel-specs', 'data')],
    [Input('simple-update', 'n_clicks'),
     Input('advanced-update', 'n_clicks'),
     Input('results-replot', 'n_clicks'),
     State('table-results', 'data'),
     State('fuel-specs', 'data'),
     State("plotting-config", "data"),
     State('simple-gwp', 'value'),
     State('simple-leakage', 'value'),
     State('simple-ng-price', 'value'),
     State('simple-lifetime', 'value'),
     State('simple-irate', 'value'),
     State('simple-cost-green-capex-2020', 'value'),
     State('simple-cost-green-capex-2050', 'value'),
     State('simple-cost-green-elec-2020', 'value'),
     State('simple-cost-green-elec-2050', 'value'),
     State('simple-green-ocf', 'value'),
     State('simple-elecsrc', 'value'),
     State('simple-elecsrc-custom', 'value'),
     State('simple-cost-blue-capex-heb', 'value'),
     State('simple-cost-blue-capex-leb', 'value'),
     State('simple-cost-blue-cts-2020', 'value'),
     State('simple-cost-blue-cts-2050', 'value'),
     State('simple-cost-blue-eff-heb', 'value'),
     State('simple-cost-blue-eff-leb', 'value'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data')])
def callbackUpdate(n1, n2, n3, table_results_data, fuel_specs_data, plotting_cfg: dict, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        scenarioInputUpdated = scenarioInputDefault.copy()
        fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenarioInputUpdated)
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-update':
            scenarioInputUpdated = updateScenarioInputSimple(scenarioInputDefault.copy(), *args)
            fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenarioInputUpdated)
        elif btnPressed == 'advanced-update':
            scenarioInputUpdated = updateScenarioInputAdvanced(scenarioInputDefault.copy(), *args)
            fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenarioInputUpdated)
        elif btnPressed == 'results-replot':
            fuelData = pd.DataFrame(table_results_data)
            fuelData['year'] = fuelData['year'].astype(int)
            fuelData['cost'] = fuelData['cost'].astype(float)
            fuelData['cost_u'] = fuelData['cost_u'].astype(float)
            fuelData['ci'] = fuelData['ci'].astype(float)
            fuelData['ci_u'] = fuelData['ci_u'].astype(float)
            fuelSpecs = fuel_specs_data
            FSCPData = calcFSCPs(fuelData)
        else:
            raise Exception("Unknown button pressed!")

    fig1 = plotFig1(fuelData, fuelSpecs, FSCPData, plotting_cfg['fig1'], export_img=False)

    showFuels = ['green RE',
                 'green mix',
                 'blue HEB',
                 'blue LEB']

    fig2 = plotFig2(fuelData, fuelSpecs, FSCPData,
                    refFuel = 'natural gas',
                    refYear = 2020,
                    showFuels = showFuels, export_img=False)

    showFSCPs = [
        ([1, 2], 'natural gas', 'green RE'),
        ([1], 'natural gas', 'blue HEB'),
        ([2], 'natural gas', 'blue LEB'),
        ([1], 'blue HEB', 'green RE'),
        ([2], 'blue LEB', 'green RE'),
    ]

    fig3 = plotFig3(fuelSpecs, FSCPData, showFSCPs=showFSCPs, export_img=False)

    fig4 = plotFig4(fuelData, export_img=False)
    fig5 = plotFig5(fullParams, fuelData, export_img=False)
    fig6 = plotFig6(fullParams, fuelData, export_img=False)

    return fig1, fig2, fig3, fig4, fig5, fig6, fuelData.to_dict('records'), fuelSpecs


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
     State('simple-cost-green-capex-2020', 'value'),
     State('simple-cost-green-capex-2050', 'value'),
     State('simple-cost-green-elec-2020', 'value'),
     State('simple-cost-green-elec-2050', 'value'),
     State('simple-green-ocf', 'value'),
     State('simple-elecsrc', 'value'),
     State('simple-elecsrc-custom', 'value'),
     State('simple-cost-blue-capex-heb', 'value'),
     State('simple-cost-blue-capex-leb', 'value'),
     State('simple-cost-blue-cts-2020', 'value'),
     State('simple-cost-blue-cts-2050', 'value'),
     State('simple-cost-blue-eff-heb', 'value'),
     State('simple-cost-blue-eff-leb', 'value'),
     State('advanced-gwp', 'value'),
     State('advanced-times', 'data'),
     State('advanced-fuels', 'data'),],
     prevent_initial_call=True,)
def callbackDownloadConfig(n1, n2, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise Exception("Initial call not prevented!")
    else:
        btnPressed = ctx.triggered[0]['prop_id'].split('.')[0]
        if btnPressed == 'simple-download-config':
            scenarioInputUpdated = updateScenarioInputSimple(scenarioInputDefault.copy(), *args)
        elif btnPressed == 'advanced-download-config':
            scenarioInputUpdated = updateScenarioInputAdvanced(scenarioInputDefault.copy(), *args)
        else:
            raise Exception("Unknown button pressed!")

    return dict(content=yaml.dump(scenarioInputUpdated, sort_keys=False), filename="scenario.yml")


# this callback sets the background colour of the rows in the fuel table in the advanced tab
@app.callback(
   Output(component_id='advanced-fuels', component_property='style_data_conditional'),
   [Input(component_id='advanced-fuels', component_property='data')])
def callbackWidget2(data):
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


# this callback shows/hides the custom elecsrc carbon intensity field
@app.callback(
   Output(component_id='wrapper-simple-elecsrc-custom', component_property='style'),
   [Input(component_id='simple-elecsrc', component_property='value')])
def callbackWidget1(elecsrc_selected):
    if elecsrc_selected == 'custom':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


# path for downloading XLS data file
@app.server.route("/download/data.xlsx")
def callbackDownloadExportdata():
    return send_file("output/data.xlsx", as_attachment=True)
