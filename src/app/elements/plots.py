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
    )

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

    fig3 = dbc.Card(
        id="card-fig-3",
        children=[
            dbc.CardHeader("Fig. 3"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig3',
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    )

    fig4 = dbc.Card(
        id="card-fig-4",
        children=[
            dbc.CardHeader("Fig. 4"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig4',
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    )

    fig5 = dbc.Card(
        id="card-fig-5",
        children=[
            dbc.CardHeader("Fig. 5"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig5',
                                    )
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    )

    return fig1, fig2, fig3, fig4, fig5
