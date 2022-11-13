from src.config_load import input_data, plots_cfg
from src.config_load_app import app_cfg
from src.data.data import getFullData
from src.plotting.plot_all import plotAllFigs
from src.plotting.styling.webapp import addWebappSpecificStyling

outputData = getFullData(input_data.copy())
figsNeeded = [fig for fig, routes in app_cfg['figures'].items() if '/' in routes]
figsDefault = plotAllFigs(outputData, input_data.copy(), plots_cfg, global_cfg='webapp', figs_needed=figsNeeded)
addWebappSpecificStyling(figsDefault)
