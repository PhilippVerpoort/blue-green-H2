from dash.dependencies import Input, Output, State

from server import app, scenarioInputDefault
from src.app.update import updateScenarioInputSimple, updateScenarioInputAdvanced
from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2

@app.callback(
    [Output('fig1', 'figure'),
     Output('fig2', 'figure')],
    [Input('update-scenario', 'n_clicks'),
     State('control-tabs', 'value'),
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
     State('advanced-fuels', 'data'),])
def callback1(n, c, *args):
    if c == 'simple':
        scenarioInputUpdated = updateScenarioInputSimple(scenarioInputDefault, *args)
    else:
        scenarioInputUpdated = updateScenarioInputAdvanced(scenarioInputDefault, *args)

    fuelData, FSCPData = obtainScenarioData(scenarioInputUpdated)

    showFuels = [
        ([1,2], 2020, 'natural gas'),
        ([1,2], 2020, 'green RE'),
        ([1,2], 2050, 'green RE'),
        ([1], 2020, 'blue HEB'),
        ([2], 2020, 'blue LEB'),
    ]

    showFSCPs = [
        ([1, 2], 2020, 'natural gas', 2020, 'green RE'),
        ([1, 2], 2020, 'natural gas', 2050, 'green RE'),
        ([1], 2020, 'natural gas', 2020, 'blue HEB'),
        ([1], 2020, 'blue HEB',    2020, 'green RE'),
        ([1], 2020, 'blue HEB',    2050, 'green RE'),
        ([2], 2020, 'natural gas', 2020, 'blue LEB'),
        ([2], 2020, 'blue LEB',    2020, 'green RE'),
        ([2], 2020, 'blue LEB',    2050, 'green RE'),
    ]

    fig1 = plotFig1(fuelData, FSCPData, showFuels=showFuels, showFSCPs=showFSCPs)

    showFuels = ['green RE',
                 'green mix',
                 'blue HEB',
                 'blue LEB']

    fig2 = plotFig2(fuelData, FSCPData,
                    refFuel = 'natural gas',
                    refYear = 2020,
                    showFuels = showFuels)

    return fig1, fig2

@app.callback(
   Output(component_id='wrapper-simple-elecsrc-custom', component_property='style'),
   [Input(component_id='simple-elecsrc', component_property='value')])
def callback2(elecsrc_selected):
    if elecsrc_selected == 'custom':
        return {'display': 'block'}
    else:
        return {'display': 'none'}
