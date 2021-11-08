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
