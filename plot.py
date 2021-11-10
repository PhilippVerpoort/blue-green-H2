import yaml

from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6


# obtain scenario input
scenario = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)
fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenario)

configFig1 = yaml.load(open('input/plotting/config_fig1.yml', 'r').read(), Loader=yaml.FullLoader)
plotFig1(fuelData, fuelSpecs, FSCPData, configFig1)

showFSCPs = [
    ([1, 2], 'natural gas', 'green RE'),
    ([1], 'natural gas', 'blue HEB'),
    ([2], 'natural gas', 'blue LEB'),
    ([1], 'blue HEB', 'green RE'),
    ([2], 'blue LEB', 'green RE'),
]

plotFig3(fuelSpecs, FSCPData, showFSCPs=showFSCPs)

plotFig4(fuelData)

plotFig5(fullParams, fuelData)

plotFig6(fullParams, fuelData)
