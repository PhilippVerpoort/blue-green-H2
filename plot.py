import yaml

from src.config_load import input_data, steel_data
from src.data.data import getFullData
from src.data.params.export_params import exportInputData
from src.plotting.loadcfg import loadInitialPlottingCfg
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6
from src.plotting.plotFig7 import plotFig7
from src.plotting.plotFig8 import plotFig8


# Get full parameter, fuel, FSCP, and steel data based on input data.
fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel = getFullData(input_data, steel_data)


# Export params to CSV table for presenting in the paper.
exportInputData(input_data)


# Create plots and automatically export to image files.
plotting_cfg = loadInitialPlottingCfg()
#plotFig1(fuelSpecs, fuelData, FSCPData, yaml.load(plotting_cfg['fig1'], Loader=yaml.FullLoader))
#plotFig2(fuelSpecs, fuelData, yaml.load(plotting_cfg['fig2'], Loader=yaml.FullLoader))
plotFig3(fuelSpecs, FSCPData, FSCPDataSteel, yaml.load(plotting_cfg['fig3'], Loader=yaml.FullLoader))
#plotFig4(fuelSpecs, fuelData, fuelDataSteel, yaml.load(plotting_cfg['fig4'], Loader=yaml.FullLoader))
#plotFig5(fuelSpecs, fuelData, fullParams, input_data['fuels'], yaml.load(plotting_cfg['fig5'], Loader=yaml.FullLoader))
#plotFig6(fullParams, input_data['fuels'], yaml.load(plotting_cfg['fig6'], Loader=yaml.FullLoader))
#plotFig7(fuelSpecs, input_data, fullParams, yaml.load(plotting_cfg['fig7'], Loader=yaml.FullLoader))
#plotFig8(fuelSpecs, input_data, fullParams, yaml.load(plotting_cfg['fig8'], Loader=yaml.FullLoader))
