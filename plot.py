import yaml

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
plotFig1(fuelData, fuelSpecs, FSCPData, yaml.load(plotting_cfg['fig1'], Loader=yaml.FullLoader))
plotFig2(fuelData, fuelSpecs, FSCPData, yaml.load(plotting_cfg['fig2'], Loader=yaml.FullLoader))
plotFig3(fuelSpecs, FSCPData, yaml.load(plotting_cfg['fig3'], Loader=yaml.FullLoader))
plotFig4(fuelSpecs, fuelData, yaml.load(plotting_cfg['fig4'], Loader=yaml.FullLoader))
plotFig5(fullParams, scenario['fuels'], 'gwp100', yaml.load(plotting_cfg['fig5'], Loader=yaml.FullLoader))
plotFig6(fullParams, scenario['fuels'], yaml.load(plotting_cfg['fig6'], Loader=yaml.FullLoader))
plotFig7(fuelSpecs, scenario, fullParams, yaml.load(plotting_cfg['fig7'], Loader=yaml.FullLoader))
