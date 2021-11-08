import yaml

from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1

scenarioData = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)

fuelData, FSCPData = obtainScenarioData(scenarioData)

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

plotFig1(fuelData, FSCPData, showFuels=showFuels, showFSCPs=showFSCPs)
