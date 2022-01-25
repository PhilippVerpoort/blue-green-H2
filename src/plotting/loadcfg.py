from src.filepaths import getFilePathInput

n_figs = 8

def loadInitialPlottingCfg():
    cfg = {}
    for f in range(1, n_figs+1):
        filePath = getFilePathInput(f"plotting/config_fig{f}.yml")
        cfg[f"fig{f}"] = open(filePath, 'r').read()
    return cfg
