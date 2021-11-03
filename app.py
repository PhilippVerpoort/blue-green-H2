# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import yaml
from dash import dcc, html
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from src.data.data import obtainScenarioData
from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2


# define Dash app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.title = "Blue-green hydrogen competition"



# compute data
scenarioData = yaml.load(open('input/data/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)


@app.callback(
    Output('fig1', 'figure'),
    [Input('widget-gwp', 'value'), Input('widget-leakage', 'value')])
def update_fig1(gwp, lr):
    scenarioData['params']['gwp']['value'] = 100.0 if gwp=='gwp100' else 20
    for fuel in scenarioData['fuels']:
        if scenarioData['fuels'][fuel]['type'] not in ['ng', 'blue']: continue
        scenarioData['fuels'][fuel]['methane_leakage'] = lr/100

    fuelData, FSCPData = obtainScenarioData(scenarioData)

    showFuels = [
        ([1,2], 2020, 'natural gas'),
        ([1,2], 2020, 'green RE'),
        ([1,2], 2050, 'green RE'),
        ([1], 2020, 'blue HEB'),
        ([2], 2020, 'blue LEB'),
    ]

    showFSCPs = [
        ([1, 2], 2020, 'natural gas', 2020, 'green RE'),
        ([1, 2], 2020, 'natural gas', 2050, 'green RE'),
        # ([1], 2020, 'natural gas', 2020, 'blue HEB'),
        ([1], 2020, 'blue HEB',    2020, 'green RE'),
        ([1], 2020, 'blue HEB',    2050, 'green RE'),
        ([2], 2020, 'natural gas', 2020, 'blue LEB'),
        ([2], 2020, 'blue LEB',    2020, 'green RE'),
        ([2], 2020, 'blue LEB',    2050, 'green RE'),
    ]

    fig = plotFig1(fuelData, FSCPData, showFuels=showFuels, showFSCPs=showFSCPs)

    return fig



@app.callback(
    Output('fig2', 'figure'),
    [Input('widget-gwp', 'value'), Input('widget-leakage', 'value')])
def update_fig2(gwp, lr):
    scenarioData['params']['gwp']['value'] = 100.0 if gwp=='gwp100' else 20
    for fuel in scenarioData['fuels']:
        if scenarioData['fuels'][fuel]['type'] not in ['ng', 'blue']: continue
        scenarioData['fuels'][fuel]['methane_leakage'] = lr/100

    fuelData, FSCPData = obtainScenarioData(scenarioData)

    showFuels = [
        ([1,2], 2020, 'natural gas'),
        ([1,2], 2020, 'green RE'),
        ([1,2], 2050, 'green RE'),
        ([1], 2020, 'blue HEB'),
        ([2], 2020, 'blue LEB'),
    ]

    fig = plotFig2(fuelData, FSCPData,
                   refFuel = 'natural gas',
                   refYear = 2020,
                   showFuels = ['green RE', 'blue HEB', 'blue LEB'])

    return fig



button_howto = dbc.Button(
    "Learn more",
    id="howto-open",
    outline=True,
    color="info",
    href="https://www.pik-potsdam.de/",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

button_github = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/PhilippVerpoort/",
    id="gh-link",
    style={"text-transform": "none"},
)

# Header
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            id="logo",
                            src=app.get_asset_url("logo.png"),
                            height="30px",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Blue-green hydrogen competition"),
                                    html.P("An interactive plotting widget"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    ),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(button_howto),
                                        dbc.NavItem(button_github),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),
                        ],
                        md=2,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
)

# Description
description = dbc.Col(
    [
        dbc.Card(
            id="description-card",
            children=[
                dbc.CardHeader("Explanation"),
                dbc.CardBody(
                    [
                        html.P(
                            "These graphs show analysis of the competition between blue and green hydrogen. They are also used in publication XYZ."
                            "You can adjust the numbers and see how things change. Enjoy. :)"
                        ),
                    ]
                ),
            ],
        )
    ],
    md=12,
)

# Image Segmentation
segmentation = [
    dbc.Card(
        id="card-fig-1",
        children=[
            dbc.CardHeader("Viewer"),
            dbc.CardBody(
                [
                    # Wrap dcc.Loading in a div to force transparency when loading
                    html.Div(
                        id="transparent-loader-wrapper-fig1",
                        children=[
                            dcc.Loading(
                                id="segmentations-loading-fig1",
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig1',
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    ),
    dbc.Card(
        id="card-fig-2",
        children=[
            dbc.CardHeader("Viewer"),
            dbc.CardBody(
                [
                    # Wrap dcc.Loading in a div to force transparency when loading
                    html.Div(
                        id="transparent-loader-wrapper-fig2",
                        children=[
                            dcc.Loading(
                                id="segmentations-loading-fig2",
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig2',
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    )
]

# sidebar
sidebar = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Parameters"),
            dbc.CardBody(
                [
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Select GWP",
                                        html_for="widget-gwp",
                                    ),
                                    dcc.RadioItems(
                                        id="widget-gwp",
                                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                                        value='gwp100',
                                    ),
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Leakage Rate in %",
                                        html_for="widget-leakage",
                                    ),
                                    daq.NumericInput(
                                        id="widget-leakage",
                                        min=0,
                                        max=100,
                                        value=2,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ],
    ),
]

meta = [
    html.Div(
        id="no-display",
        children=[
            # Store for user created masks
            # data is a list of dicts describing shapes
            dcc.Store(id="masks", data={"shapes": []}),
            dcc.Store(id="classifier-store", data={}),
            dcc.Store(id="classified-image-store", data=""),
            dcc.Store(id="features_hash", data=""),
        ],
    ),
    html.Div(id="download-dummy"),
    html.Div(id="download-image-dummy"),
]

app.layout = html.Div(
    [
        header,
        dbc.Container(
            [
                dbc.Row(description),
                dbc.Row(
                    id="app-content",
                    children=[dbc.Col(sidebar, md=4), dbc.Col(segmentation, md=8)],
                ),
                dbc.Row(dbc.Col(meta)),
            ],
            fluid=True,
        ),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
