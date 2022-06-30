import sys

from src.config_load import input_data, plots_cfg
from src.data.data import getFullData, exportDataXLS
from src.data.params.export_params import exportInputData
from src.plotting.export_file import exportFigsToFiles
from src.plotting.plot_all import plotAllFigs


# Get list of figs to plot from command line args.
if len(sys.argv) > 1:
    plot_list = sys.argv[1:]
else:
    plot_list = None


# Get full parameter, fuel, FSCP, and steel data based on input data.
outputData = getFullData(input_data)


# Export params to CSV table for presenting in the paper.
exportInputData(input_data['params'])


# export selected input and output data as XLS
exportDataXLS(input_data, outputData)


# Run plotting routines to generate figures
figs = plotAllFigs(outputData, input_data, plots_cfg, plot_list=plot_list)


# Export figures to files
exportFigsToFiles(figs)
