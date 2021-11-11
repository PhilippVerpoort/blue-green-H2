import yaml

n_figs = 7

def loadInitialPlottingCfg():
    cfg = {}
    for f in range(1, n_figs+1):
        cfg[f"fig{f}"] = yaml.load(open(f"input/plotting/config_fig{f}.yml", 'r').read(),
                                   Loader=yaml.FullLoader)
    return cfg
