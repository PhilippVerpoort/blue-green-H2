import yaml

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from src.config_load import input_data


def getElementAdvancedControlsCardRight():
    fuels = input_data['fuels']
    fuels_data = [
        dict(
            fuel=fuel,
            desc=fuels[fuel]['name'],
            colour=fuels[fuel]['colour'],
        ) for fuel in fuels
    ]

    params = input_data['params']
    params_data = [dict(param=param,
                       desc=params[param]['desc'],
                       type=params[param]['type'],
                       value=yaml.dump(params[param]['value']) if isinstance(params[param]['value'], dict) else params[param]['value'],
                       unit=params[param]['unit']
                       ) for param in params]
    

    widget_advanced_params = html.Div(
        children=[
            dbc.Label(
                'Parameters',
                html_for='advanced-params',
            ),
            dash_table.DataTable(
                id='advanced-params',
                columns=[
                    {'id': 'param', 'name': 'ID', 'editable': False},
                    {'id': 'desc', 'name': 'Name', 'editable': False},
                    {'id': 'type', 'name': 'Type', 'presentation': 'dropdown', 'editable': True},
                    {'id': 'value', 'name': 'Value', 'editable': False},
                    {'id': 'unit', 'name': 'Unit', 'editable': False},
                ],
                data=params_data,
                editable=True,
                dropdown={
                    'type': {
                        'options': [
                            {'value': 'const', 'label': 'Constant'},
                            {'value': 'linear', 'label': 'Linear'},
                        ]
                    }
                },
                style_cell={'whiteSpace': 'pre-line'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'param'},
                        'display': 'none',
                    },
                    {
                        'if': {'column_id': 'desc'},
                        'width': '35%',
                    },
                    {
                        'if': {'column_id': 'type'},
                        'width': '10%',
                    },
                    {
                        'if': {'column_id': 'value'},
                        'width': '45%',
                    },
                    {
                        'if': {'column_id': 'unit'},
                        'width': '10%',
                    },
                ],
            ),
        ],
        className='card-element',
    )

    return html.Div(
        id='advanced-controls-card-right',
        className='side-card',
        children=[
            widget_advanced_params,
        ],
        style={'display': 'none'},
    )
