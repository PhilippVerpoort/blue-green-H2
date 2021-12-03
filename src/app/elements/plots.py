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
                            ),
                            dbc.Button(id='fig1-settings', children='Plot config', className='scenario-buttons'),
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
                            ),
                            dbc.Button(id='fig2-settings', children='Plot config', className='scenario-buttons'),
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
                            ),
                            dbc.Button(id='fig3-settings', children='Plot config', className='scenario-buttons'),
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
                            ),
                            dbc.Button(id='fig4-settings', children='Plot config', className='scenario-buttons'),
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
                            ),
                            dbc.Button(id='fig5-settings', children='Plot config', className='scenario-buttons'),
                        ],
                    ),
                ]
            ),
        ],
    )

    fig6 = dbc.Card(
        id="card-fig-6",
        children=[
            dbc.CardHeader("Fig. 6"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig6',
                                    )
                                ],
                            ),
                            dbc.Button(id='fig6-settings', children='Plot config', className='scenario-buttons'),
                        ],
                    ),
                ]
            ),
        ],
    )

    fig7 = dbc.Card(
        id="card-fig-7",
        children=[
            dbc.CardHeader("Fig. 7"),
            dbc.CardBody(
                [
                    html.Div(
                        children=[
                            dcc.Loading(
                                type="circle",
                                children=[
                                    dcc.Graph(
                                        id='fig7',
                                    )
                                ],
                            ),
                            dbc.Button(id='fig7-settings', children='Plot config', className='scenario-buttons'),
                        ],
                    ),
                ]
            ),
        ],
    )

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7
