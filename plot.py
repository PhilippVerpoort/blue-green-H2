from src.config_load import input_data, steel_data, plotting_cfg
from src.data.data import getFullData
from src.data.params.export_params import exportInputData
from src.plotting.plotAllFigs import plotAllFigs


# Get full parameter, fuel, FSCP, and steel data based on input data.
fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel = getFullData(input_data, steel_data)


# Export params to CSV table for presenting in the paper.
exportInputData(input_data)


# Create plots and automatically export to image files.
plotAllFigs(fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel, input_data, plotting_cfg)
