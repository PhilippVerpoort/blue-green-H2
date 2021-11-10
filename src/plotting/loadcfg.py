import yaml

def loadInitialPlottingCfg():
    cfg = {}
    for f in range(1, 7):
        cfg[f"fig{f}"] = yaml.load(open(f"input/plotting/config_fig{f}.yml", 'r').read(),
                                            Loader=yaml.FullLoader)
    return cfg
