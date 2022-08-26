from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from src.app.callbacks.simple_params import getSimpleParamsTable, cons_vs_prog_params, gas_prices_params


def getElementSimpleControlsCard():
    return html.Div(
        id='simple-controls-card',
        children=[
            html.Div(
                [
                    dbc.Label(
                        'Most important parameters and selected cases:',
                        html_for='simple-important-params',
                    ),
                    dash_table.DataTable(
                        id='simple-important-params',
                        columns=[
                            {'id': 'name', 'name': 'Name', 'editable': False,},
                            {'id': 'desc', 'name': 'Parameter', 'editable': False,},
                            {'id': 'unit', 'name': 'Unit', 'editable': False,},
                            {'id': 'cons', 'name': 'Conservative cases'},
                            {'id': 'prog', 'name': 'Proressive cases'},
                        ],
                        data=getSimpleParamsTable(cons_vs_prog_params, ['cons', 'prog'], 'cons_vs_prog'),
                        editable=False,
                        style_cell={'whiteSpace': 'pre-line'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'name'},
                                'display': 'none',
                            },
                            {
                                'if': {'column_id': 'desc'},
                                'width': '25%',
                            },
                            {
                                'if': {'column_id': 'unit'},
                                'width': '15%',
                            },
                            {
                                'if': {'column_id': 'cons'},
                                'width': '30%',
                            },
                            {
                                'if': {'column_id': 'prog'},
                                'width': '30%',
                            },
                        ],
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                [
                    dbc.Label(
                        'Gas price cases:',
                        html_for='simple-gas-prices',
                    ),
                    dash_table.DataTable(
                        id='simple-gas-prices',
                        columns=[
                            {'id': 'name', 'name': 'Name', 'editable': False,},
                            {'id': 'desc', 'name': 'Parameter', 'editable': False,},
                            {'id': 'unit', 'name': 'Unit', 'editable': False,},
                            {'id': 'high', 'name': 'High price'},
                            {'id': 'low', 'name': 'Low price'},
                        ],
                        data=getSimpleParamsTable(gas_prices_params, ['high', 'low'], 'gas_prices'),
                        editable=False,
                        style_cell={'whiteSpace': 'pre-line'},
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'name'},
                                'display': 'none',
                            },
                            {
                                'if': {'column_id': 'desc'},
                                'width': '25%',
                            },
                            {
                                'if': {'column_id': 'unit'},
                                'width': '15%',
                            },
                            {
                                'if': {'column_id': 'cons'},
                                'width': '30%',
                            },
                            {
                                'if': {'column_id': 'prog'},
                                'width': '30%',
                            },
                        ],
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                [
                    dbc.Label(
                        'Global Warming Potential (GWP) reference time scale:',
                        html_for='simple-gwp',
                    ),
                    dcc.RadioItems(
                        id='simple-gwp',
                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                        value='gwp100',
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                children=[
                    html.Button(id='simple-update', n_clicks=0, children='Update', className='scenario-buttons'),
                    html.Button(id='download-config', n_clicks=0, children='Download config', className='scenario-buttons'),
                    html.Form(
                        action='/download/data.xlsx',
                        method='get',
                        children=[
                            dbc.Button(id='results-download', type='submit', children='Download data', className='scenario-buttons')
                        ],
                        style={'float': 'right'},
                    ),
                ],
                className='card-element',
            ),
        ],
        className='side-card',
    )
