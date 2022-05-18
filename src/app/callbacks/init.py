from config_load import input_data, steel_data, plots_cfg
from data.data import getFullData
from plotting.plot_all import plotAllFigs


outputData = getFullData(input_data.copy(), steel_data)
figsDefault = plotAllFigs(outputData, input_data.copy(), plots_cfg, global_cfg='webapp')
