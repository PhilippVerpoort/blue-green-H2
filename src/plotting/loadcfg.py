from src.filepaths import getFilePathInputs

n_figs = 7

def loadInitialPlottingCfg():
    cfg = {}
    for f in range(1, n_figs+1):
        filePath = getFilePathInputs(f"plotting/config_fig{f}.yml")
        cfg[f"fig{f}"] = open(filePath, 'r').read()
    return cfg
