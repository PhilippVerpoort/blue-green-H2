import os

import dash
import yaml
import dash_bootstrap_components as dbc

from src.app.layout import setLayout

# define Dash app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Blue-green hydrogen competition"

# define server
server = app.server

# define current working directory
cwd = os.getcwd()

# load scenario default input data
scenarioInputDefault = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)

# define layout
setLayout(app, scenarioInputDefault)
