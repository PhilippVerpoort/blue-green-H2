import yaml

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from src.config_load import input_data


def getElementAdvancedControlsCardLeft():
    return html.Div(
        id='advanced-controls-card-left',
        children=[
            html.Div(
                [
                    dbc.Label(
                        'Global Warming Potential (GWP) reference time scale:',
                        html_for='advanced-gwp',
                    ),
                    dcc.RadioItems(
                        id='advanced-gwp',
                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                        value='gwp100',
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                [
                    dbc.Label(
                        'Time steps:',
                        html_for='advanced-times',
                    ),
                    dash_table.DataTable(
                        id='advanced-times',
                        columns=[{'id': 'i', 'name': 'Time steps'}],
                        data=[dict(i=t) for t in input_data['options']['times']],
                        editable=True
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                children=[
                    html.Button(id='advanced-update', n_clicks=0, children='Update', className='scenario-buttons'),
                    html.Button(id='advanced-download-config', n_clicks=0, children='Download Config', className='scenario-buttons'),
                ],
                className='card-element',
            ),
        ],
        className='side-card elements-card',
        style={'display': 'none'},
    )


def getElementAdvancedControlsCardRight():
    fuels = input_data['fuels']
    fuels_data = [dict(fuel=fuel,
                       desc=fuels[fuel]['desc'],
                       colour=fuels[fuel]['colour'],
                       type=fuels[fuel]['type'],
                       tech_type=fuels[fuel]['tech_type'] if 'tech_type' in fuels[fuel] else None,
                       include_capex=fuels[fuel]['include_capex'] if 'include_capex' in fuels[fuel] else None,
                       ) for fuel in fuels]

    widget_advanced_fuels = html.Div(
        children=[
            dbc.Label(
                'Fuels',
                html_for='advanced-fuels',
            ),
            dash_table.DataTable(
                id='advanced-fuels',
                columns=[
                    {'id': 'fuel', 'name': 'Fuel ID'},
                    {'id': 'desc', 'name': 'Fuel name'},
                    {'id': 'colour', 'name': 'Colour'},
                    {'id': 'type', 'name': 'Fuel type', 'presentation': 'dropdown'},
                    {'id': 'tech_type', 'name': 'Tech type', 'presentation': 'dropdown'},
                    {'id': 'include_capex', 'name': 'Include CAPEX', 'presentation': 'dropdown'},
                ],
                data=fuels_data,
                editable=True,
                dropdown={
                    'type': {
                        'options': [
                            {'value': 'ng', 'label': 'Natural Gas'},
                            {'value': 'blue', 'label': 'Blue Hydrogen'},
                            {'value': 'green', 'label': 'Green Hydrogen'},
                        ]
                    },
                    'tech_type': {
                        'options': [
                            {'value': 'smr', 'label': 'SMR only'},
                            {'value': 'smr+lcrccs', 'label': 'SMR+LCRCCS'},
                            {'value': 'smr+hcrccs', 'label': 'SMR+HCRCCS'},
                            {'value': 'atr+hcrccs', 'label': 'ATR+HCRCCS'},
                            {'value': 'RE', 'label': 'RE only'},
                            {'value': 'grid', 'label': 'Grid elec.'},
                        ]
                    },
                    'include_capex': {
                        'options': [
                            {'value': True, 'label': 'True'},
                            {'value': False, 'label': 'False'},
                        ]
                    },
                }
            ),
            html.Div(id='table-fuels-dropdown-container'),
        ],
        className='card-element',
    )

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
            html.Div(id='table-params-dropdown-container'),
        ],
        className='card-element',
    )

    return html.Div(
        id='advanced-controls-card-right',
        className='fig-card',
        children=[
            widget_advanced_fuels,
            widget_advanced_params,
        ],
        style={'display': 'none'},
    )
