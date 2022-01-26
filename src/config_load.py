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
