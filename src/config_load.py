import yaml

from src.filepaths import getFilePathInput


# load input data for calculations
__filePath = getFilePathInput('data/options.yml')
options = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
__filePath = getFilePathInput('data/fuels.yml')
fuels = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
__filePath = getFilePathInput('data/params.yml')
params = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
input_data = {**options, **fuels, **params}

__filePath = getFilePathInput('data/units.yml')
units = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)['units']

__filePath = getFilePathInput('data/steel.yml')
steel_data = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)


# load config data for plots and figures
__filePath = getFilePathInput('plots.yml')
plots = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

__filePath = getFilePathInput('figure_print.yml')
figure_print = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

__filePath = getFilePathInput('plotting/global.yml')
plots_cfg_global = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

plotting_cfg = {} # TODO: rename into plots_cfg (for consistency)
for plotName in plots:
    __filePath = getFilePathInput(f"plotting/{plotName}.yml")
    plotting_cfg[plotName] = open(__filePath, 'r').read()
