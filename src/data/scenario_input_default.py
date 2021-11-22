import yaml

from src.filepaths import getFilePathInputs

filePath = getFilePathInputs('data/scenario_default.yml')
scenarioInputDefault = yaml.load(open(filePath, 'r').read(), Loader=yaml.FullLoader)
