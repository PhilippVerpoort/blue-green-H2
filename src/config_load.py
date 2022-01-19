import yaml

from src.filepaths import getFilePathInput


__filePath = getFilePathInput('data/steel.yml')
steel_data = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
