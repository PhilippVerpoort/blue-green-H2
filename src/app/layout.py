from dash import dcc, html
import dash_bootstrap_components as dbc

from src.app.elements.header import getHeader
from src.app.elements.simple import getSimpleWidgets
from src.app.elements.advanced import getAdvancedWidgets
from src.app.elements.plots import getPlots


def setLayout(app, scenarioInputDefault):
    header = getHeader(app)

    # simple config widgets
    widget_advanced_options, widget_advanced_fuels = getAdvancedWidgets(scenarioInputDefault)

    # advanced scenario config
    widget_simple_options, widget_simple_green, widget_simple_blue = getSimpleWidgets(scenarioInputDefault)

    # plots
    fig1, fig2 = getPlots()

    # explanation
    explanation = dbc.Col(
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

    # define app layout
    app.layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    dbc.Row(explanation),
                    dbc.Row(
                        dbc.Col(
                            dcc.Tabs(id='control-tabs', value='simple', children=[
                                    dcc.Tab(
                                        label='Simple scenario config',
                                        value='simple',
                                        children=[
                                            dbc.Container(
                                                id='controls-container-simple',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(widget_simple_options, md=2),
                                                            dbc.Col(widget_simple_green, md=5),
                                                            dbc.Col(widget_simple_blue, md=5),
                                                        ],
                                                    ),
                                                ]
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Advanced scenario config',
                                        value='advanced',
                                        children=[
                                            dbc.Container(
                                                id='controls-container-advanced',
                                                children=[
                                                    dbc.Row(
                                                        children=[dbc.Col(widget_advanced_options, md=2)],
                                                    ),
                                                    dbc.Row(
                                                        children=[dbc.Col(widget_advanced_fuels, md=12)],
                                                    )
                                                ]
                                            )
                                        ],
                                    )
                                ]
                            ),
                            md = 12
                        )
                    ),
                    dbc.Row(children=[
                        dbc.Col(children=[
                                dbc.Button(id='update-scenario', n_clicks=0, children='Update Plots'),
                                dbc.Button(id='download-scenario', n_clicks=0, children='Download Config')
                            ],
                            md=4
                        ),
                    ]),
                    dbc.Row(
                        children=[dbc.Col(fig1, md=7), dbc.Col(fig2, md=5)],
                    ),
                ],
                fluid=True,
            ),
        ]
    )
