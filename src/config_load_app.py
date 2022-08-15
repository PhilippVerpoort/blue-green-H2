import yaml

from src.config_load import plots
from src.filepaths import getFilePathInput


# load config for app
__filePath = getFilePathInput('app.yml')
app_cfg = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)

figNames = [figName for plotName in plots for figName in plots[plotName]]
subfigsDisplayed = []
for plotName in plots:
    for figName in plots[plotName]:
        if figName in app_cfg['figures']:
            subfigsDisplayed.extend(plots[plotName][figName])

figs_cfg = {}
for figList in plots.values():
    for figName in figList:
        __filePath = getFilePathInput(f"figures/{figName}.yml")
        figs_cfg[figName] = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
