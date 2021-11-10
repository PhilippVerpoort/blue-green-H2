import yaml

from src.data.data import obtainScenarioData
from src.plotting.loadcfg import loadInitialPlottingCfg
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6


# load scenario and compute data
scenario = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)
fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenario)

# load plotting cfg
plotting_cfg = loadInitialPlottingCfg()

# create plots (and automatically export to files)
plotFig1(fuelData, fuelSpecs, FSCPData, plotting_cfg['fig1'])
plotFig2(fuelData, fuelSpecs, FSCPData, plotting_cfg['fig2'])
plotFig3(fuelSpecs, FSCPData, plotting_cfg['fig3'])
plotFig4(fuelData)
plotFig5(fullParams, fuelData)
plotFig6(fullParams, fuelData)
