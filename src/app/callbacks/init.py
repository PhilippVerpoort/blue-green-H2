from src.config_load import input_data, plots_cfg
from src.data.data import getFullData
from src.plotting.plot_all import plotAllFigs


outputData = getFullData(input_data.copy())
figsDefault = plotAllFigs(outputData, input_data.copy(), plots_cfg, global_cfg='webapp')
