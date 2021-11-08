from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def getSimpleWidgets(scenarioInputDefault: dict):
    widget_simple_options = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Options"),
                    dbc.CardBody(
                        children=[
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Select GWP:",
                                        html_for="simple-gwp",
                                    ),
                                    dcc.RadioItems(
                                        id="simple-gwp",
                                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                                        value='gwp100',
                                    ),
                                ]
                            ),
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Methane leakage in %:",
                                        html_for="simple-leakage",
                                    ),
                                    dcc.Input(
                                        id='simple-leakage',
                                        type='number',
                                        value=scenarioInputDefault['fuels']['natural gas']['methane_leakage']*100,
                                        step=0.05,
                                        style={'float': 'left'},
                                        placeholder='xx.x',
                                        size="5",
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )

    widget_simple_green = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Green parameters"),
                    dbc.CardBody(children=[
                        dbc.FormGroup(
                            [
                                dbc.Label(
                                    "Green CAPEX in {}:".format(scenarioInputDefault['params']['cost_green_capex']['unit']),
                                    html_for="simple-green-capex",
                                    className='display-inline-lhs',
                                ),
                                dcc.Input(
                                    id='simple-green-capex',
                                    type='number',
                                    value=scenarioInputDefault['params']['cost_green_capex']['value'][2020],
                                    step=10,
                                    style={'float': 'right'},
                                    placeholder='xx.x',
                                    size="10",
                                ),
                            ]
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label(
                                    "Green electricity cost in :",
                                    html_for="simple-green-fc",
                                    className='display-inline-lhs',
                                ),
                                dcc.Input(
                                    id='simple-green-fc',
                                    type='number',
                                    value=scenarioInputDefault['params']['cost_green_capex']['value'][2020],
                                    step=10,
                                    style={'float': 'right'},
                                    placeholder='xx.x',
                                    size="10",
                                ),
                            ]
                        ),
                    ]
                    )
                ]
            )
        ]
    )

    return widget_simple_options, widget_simple_green
