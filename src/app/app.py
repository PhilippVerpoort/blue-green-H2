import dash
import dash_bootstrap_components as dbc


# define Dash app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Blue-green hydrogen competition"


# define server
server = app.server
