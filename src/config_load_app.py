import yaml

from src.config_load import plots
from src.filepaths import getFilePathInput


# load config for webapp
__filePath = getFilePathInput('webapp.yml')
app_cfg = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)


# generate lists of figure names and subfigure names from config
figNames = [figName for plotName in plots for figName in plots[plotName]]
subfigsDisplayed = []
for plotName in plots:
    for figName in plots[plotName]:
        if figName in app_cfg['figures']:
            subfigsDisplayed.extend(plots[plotName][figName])


# load display configs of figures in webapp
__filePath = getFilePathInput(f"figure_config/webapp.yml")
figs_cfg = yaml.load(open(__filePath, 'r').read(), Loader=yaml.FullLoader)
