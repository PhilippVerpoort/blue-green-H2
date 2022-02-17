import yaml

from src.filepaths import getFilePathInput


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

plotting_cfg = {
    'fig1ab': None,
    'fig2': None,
    'fig3': None,
    'fig4': None,
    'fig5': None,
    'fig6': None,
}
for plotName in plotting_cfg:
    __filePath = getFilePathInput(f"plotting/config_{plotName}.yml")
    plotting_cfg[plotName] = open(__filePath, 'r').read()
