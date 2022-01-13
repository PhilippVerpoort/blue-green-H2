import yaml

from src.filepaths import getFilePathInput

filePath = getFilePathInput('data/scenario_default.yml')
scenarioInputDefault = yaml.load(open(filePath, 'r').read(), Loader=yaml.FullLoader)
