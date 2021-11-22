import yaml

from src.filepaths import getFilePathInputs

n_figs = 7

def loadInitialPlottingCfg():
    cfg = {}
    for f in range(1, n_figs+1):
        filePath = getFilePathInputs(f"plotting/config_fig{f}.yml")
        cfg[f"fig{f}"] = yaml.load(open(filePath, 'r').read(), Loader=yaml.FullLoader)
    return cfg
