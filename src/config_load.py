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

params_options = {pkey: pval['options'] if 'options' in pval else [] for pkey, pval in params['params'].items()}

__filePath = getFilePathInput('data/units.yml')
units = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)['units']


# load config data for plots and figures
__filePath = getFilePathInput('plots.yml')
plots = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
for plotName in plots:
    if isinstance(plots[plotName], list):
        plots[plotName] = {f: [f] for f in plots[plotName]}

__filePath = getFilePathInput('figure_config/print.yml')
figure_print = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

__filePath = getFilePathInput('plot_config/global.yml')
plots_cfg_global = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

__filePath = getFilePathInput('plot_config/co2price_traj.yml')
co2price_traj = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

plots_cfg = {}
for plotName in plots:
    __filePath = getFilePathInput(f"plot_config/{plotName}.yml")
    plots_cfg[plotName] = open(__filePath, 'r').read()


# gwp labels
__filePath = getFilePathInput(f"plot_config/gwp_labels.yml")
gwp_labels = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
