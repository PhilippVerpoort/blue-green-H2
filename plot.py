import yaml

from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4

scenarioData = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)

fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenarioData)

showFuels = [
    ([1, 2], 2020, 'natural gas'),
    ([1, 2], 2020, 'green RE'),
    ([1, 2], 2050, 'green RE'),
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

plotFig1(fuelData, fuelSpecs, FSCPData, showFuels=showFuels, showFSCPs=showFSCPs)

showFSCPs = [
    ([1, 2], 'natural gas', 'green RE'),
    ([1], 'natural gas', 'blue HEB'),
    ([2], 'natural gas', 'blue LEB'),
    ([1], 'blue HEB', 'green RE'),
    ([2], 'blue LEB', 'green RE'),
]

plotFig3(fuelSpecs, FSCPData, showFSCPs=showFSCPs)

plotFig4(scenarioData['params'], fuelData)
