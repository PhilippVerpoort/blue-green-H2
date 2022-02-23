import dash
import dash_bootstrap_components as dbc

from src.config_load_app import app_cfg


# define Dash app
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/base.css', 'assets/pik-interactive.css'],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
)
dash_app.title = app_cfg['title']
