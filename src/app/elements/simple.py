from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def getSimpleWidgets(scenarioInputDefault: dict):
    widget_simple_options = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("General options"),
                    dbc.CardBody(
                        children=[
                            html.Div(
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
                            html.Div(
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
                            html.Div(
                                className="clearfix"
                            ),
                            html.Div(
                                [
                                    dbc.Label(
                                        f"{scenarioInputDefault['params']['cost_ng_price']['desc']} in {scenarioInputDefault['params']['cost_ng_price']['unit']}:",
                                        html_for="simple-ng-price",
                                    ),
                                    dcc.Input(
                                        id='simple-ng-price',
                                        type='number',
                                        value=scenarioInputDefault['params']['cost_ng_price']['value'],
                                        step=0.1,
                                        style={'float': 'left'},
                                        placeholder='xx.x',
                                        size="5",
                                    ),
                                ]
                            ),
                            html.Div(
                                className="clearfix"
                            ),
                            html.Div(
                                [
                                    dbc.Label(
                                        "Lifetime in years:",
                                        html_for="simple-lifetime",
                                    ),
                                    dcc.Input(
                                        id='simple-lifetime',
                                        type='number',
                                        value=scenarioInputDefault['params']['lifetime']['value'],
                                        step=1,
                                        style={'float': 'left'},
                                        placeholder='xx',
                                        size="5",
                                    ),
                                ]
                            ),
                            html.Div(
                                className="clearfix"
                            ),
                            html.Div(
                                [
                                    dbc.Label(
                                        f"{scenarioInputDefault['params']['irate']['desc']} in %:",
                                        html_for="simple-irate",
                                    ),
                                    dcc.Input(
                                        id='simple-irate',
                                        type='number',
                                        value=scenarioInputDefault['params']['irate']['value']*100,
                                        step=0.1,
                                        style={'float': 'left'},
                                        placeholder='x.x',
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

    param_fields_green = {
        'cost_green_capex_2020': {
            'name': f"{scenarioInputDefault['params']['cost_green_capex']['desc']} in 2020",
            'value': scenarioInputDefault['params']['cost_green_capex']['value'][2020],
            'unit': scenarioInputDefault['params']['cost_green_capex']['unit'],
            'step': 10,
        },
        'cost_green_capex_2050': {
            'name': f"{scenarioInputDefault['params']['cost_green_capex']['desc']} in 2050",
            'value': scenarioInputDefault['params']['cost_green_capex']['value'][2050],
            'unit': scenarioInputDefault['params']['cost_green_capex']['unit'],
            'step': 10,
        },
        'cost_green_elec_2020': {
            'name': f"{scenarioInputDefault['params']['cost_green_elec']['desc']} in 2020",
            'value': scenarioInputDefault['params']['cost_green_elec']['value']['custom'][2020],
            'unit': scenarioInputDefault['params']['cost_green_elec']['unit'],
            'step': 1,
        },
        'cost_green_elec_2050': {
            'name': f"{scenarioInputDefault['params']['cost_green_elec']['desc']} in 2050",
            'value': scenarioInputDefault['params']['cost_green_elec']['value']['custom'][2050],
            'unit': scenarioInputDefault['params']['cost_green_elec']['unit'],
            'step': 1,
        },
        'green_ocf': {
            'name': scenarioInputDefault['params']['green_ocf']['desc'],
            'value': scenarioInputDefault['params']['green_ocf']['value']*100,
            'unit': "%",
            'step': 1,
        }
    }

    # green:
    # elec src (wind/solar/hydro/custom/mix)

    fields = [
        html.Div(
            [
                dbc.Label(
                    f"{param_fields_green[param]['name']} in {param_fields_green[param]['unit']}:",
                    html_for=f"simple-{param.replace('_', '-')}",
                    className='display-inline-lhs',
                ),
                dcc.Input(
                    id=f"simple-{param.replace('_', '-')}",
                    type='number',
                    value=param_fields_green[param]['value'],
                    step=param_fields_green[param]['step'],
                    style={'float': 'right'},
                    placeholder='xx',
                    size="10",
                ),
            ]
        )
        for param in param_fields_green
    ]

    elecsrc_dropdown = html.Div(
        [
            dbc.Label(
                "Carbon intensity of electricity:",
                html_for=f"simple-elecsrc",
                className='display-inline-lhs',
            ),
            dcc.Dropdown(
                id='simple-elecsrc',
                options=[
                    {'label': 'Run-of-river Hydro Power', 'value': 'hydro'},
                    {'label': 'Wind Power On-shore', 'value': 'wind'},
                    {'label': 'PV power', 'value': 'solar'},
                    {'label': 'Current EU mix', 'value': 'mix'},
                    {'label': 'Custom', 'value': 'custom'}
                ],
                value='wind',
                style={'float': 'right', 'width': '300px'},
            ),
        ]
    )
    fields.append(elecsrc_dropdown)

    custom_ci = html.Div(
        id="wrapper-simple-elecsrc-custom",
        children=[
            html.Div(
                [
                    dbc.Label(
                        f"Custom carbon intensity in {scenarioInputDefault['params']['ci_green_elec']['unit']}:",
                        html_for=f"simple-elecsrc-custom",
                        className='display-inline-lhs',
                    ),
                    dcc.Input(
                        id=f"simple-elecsrc-custom",
                        type='number',
                        value=scenarioInputDefault['params']['ci_green_elec']['value']['custom']['gwp100'],
                        step=0.001,
                        style={'float': 'right'},
                        placeholder='xx',
                        size="10",
                    ),
                ]
            )
        ],
        style={'display': 'none'}
    )
    fields.append(custom_ci)


    widget_simple_green = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Green parameters"),
                    dbc.CardBody(children=fields)
                ]
            )
        ]
    )


    param_fields_blue = {
        'cost_blue_capex_heb': {
            'name': f"{scenarioInputDefault['params']['cost_blue_capex']['desc']} of SMR+CCS",
            'value': scenarioInputDefault['params']['cost_blue_capex']['value']['heb'],
            'unit': f"{scenarioInputDefault['params']['cost_blue_capex']['unit']} per 10^5 Nm³/h",
            'step': 0.01,
        },
        'cost_blue_capex_leb': {
            'name': f"{scenarioInputDefault['params']['cost_blue_capex']['desc']} of ATR+CCS",
            'value': scenarioInputDefault['params']['cost_blue_capex']['value']['leb'],
            'unit': f"{scenarioInputDefault['params']['cost_blue_capex']['unit']} per 10^5 Nm³/h",
            'step': 0.01,
        },
        'cost_blue_cts_2020': {
            'name': f"{scenarioInputDefault['params']['cost_blue_cts']['desc']} in 2020",
            'value': scenarioInputDefault['params']['cost_blue_cts']['value'][2020],
            'unit': scenarioInputDefault['params']['cost_blue_cts']['unit'],
            'step': 1,
        },
        'cost_blue_cts_2050': {
            'name': f"{scenarioInputDefault['params']['cost_blue_cts']['desc']} in 2050",
            'value': scenarioInputDefault['params']['cost_blue_cts']['value'][2050],
            'unit': scenarioInputDefault['params']['cost_blue_cts']['unit'],
            'step': 1,
        },
        'cost_blue_eff_heb': {
            'name': f"{scenarioInputDefault['params']['cost_blue_eff']['desc']} of SMR+CCS",
            'value': scenarioInputDefault['params']['cost_blue_eff']['value']['heb'],
            'unit': scenarioInputDefault['params']['cost_blue_eff']['unit'],
            'step': 0.0001,
        },
        'cost_blue_eff_leb': {
            'name': f"{scenarioInputDefault['params']['cost_blue_eff']['desc']} of ATR+CCS",
            'value': scenarioInputDefault['params']['cost_blue_eff']['value']['leb'],
            'unit': scenarioInputDefault['params']['cost_blue_eff']['unit'],
            'step': 0.0001,
        }
    }

    fields = [
        html.Div(
            [
                dbc.Label(
                    f"{param_fields_blue[param]['name']} in {param_fields_blue[param]['unit']}:" if
                    param_fields_blue[param]['unit'] != 1 else param_fields_blue[param]['name'],
                    html_for=f"simple-{param.replace('_', '-')}",
                    className='display-inline-lhs',
                ),
                dcc.Input(
                    id=f"simple-{param.replace('_', '-')}",
                    type='number',
                    value=param_fields_blue[param]['value'],
                    step=param_fields_blue[param]['step'],
                    style={'float': 'right'},
                    placeholder='xx',
                    size="10",
                ),
            ]
        )
        for param in param_fields_blue
    ]


    widget_simple_blue = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Blue parameters"),
                    dbc.CardBody(children=fields)
                ]
            )
        ]
    )

    return widget_simple_options, widget_simple_green, widget_simple_blue
