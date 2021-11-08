from dash import html, dcc
import dash_bootstrap_components as dbc

def getPlots():
    fig1 = dbc.Card(
        id="card-fig-1",
        children=[
            dbc.CardHeader("Fig. 1"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
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

    fig2 = dbc.Card(
        id="card-fig-2",
        children=[
            dbc.CardHeader("Fig. 2"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
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

    return fig1, fig2
