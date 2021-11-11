import yaml

from src.data.calc_fuels import calcFuelData
from src.data.data import obtainScenarioData
from src.plotting.loadcfg import loadInitialPlottingCfg
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6
from src.plotting.plotFig7 import plotFig7


# load scenario and compute data
scenario = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)
fuelData, fuelSpecs, FSCPData, fullParams = obtainScenarioData(scenario)

# load plotting cfg
plotting_cfg = loadInitialPlottingCfg()

# create plots (and automatically export to files)
plotFig1(fuelData, fuelSpecs, FSCPData, plotting_cfg['fig1'])
plotFig2(fuelData, fuelSpecs, FSCPData, plotting_cfg['fig2'])
plotFig3(fuelSpecs, FSCPData, plotting_cfg['fig3'])
plotFig4(fuelSpecs, fuelData, plotting_cfg['fig4'])
plotFig5(fullParams, scenario['fuels'], 'gwp100', plotting_cfg['fig5'])
plotFig6(fullParams, scenario['fuels'], plotting_cfg['fig6'])
plotFig7(fuelSpecs, scenario, fullParams, plotting_cfg['fig7'])
