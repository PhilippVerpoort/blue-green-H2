import yaml

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def getAdvancedWidgets(scenarioInputDefault: dict):
    widget_advanced_options = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Options"),
                    dbc.CardBody(
                        children=[
                            html.Div(
                                [
                                    dbc.Label(
                                        "Select GWP:",
                                        html_for="advanced-gwp",
                                    ),
                                    dcc.RadioItems(
                                        id="advanced-gwp",
                                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                                        value='gwp100',
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    dbc.Label(
                                        "Define time intervals:",
                                        html_for="advanced-times",
                                    ),
                                    dash_table.DataTable(
                                        id="advanced-times",
                                        columns=[{'id': 'i', 'name': 'Time steps'}],
                                        data=[dict(i=t) for t in scenarioInputDefault['options']['times']],
                                        editable=True
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    
    params = scenarioInputDefault['params']
    params_data = [dict(param=param,
                       desc=params[param]['desc'],
                       type=params[param]['type'],
                       value=yaml.dump(params[param]['value']) if isinstance(params[param]['value'], dict) else params[param]['value'],
                       unit=params[param]['unit']
                       ) for param in params]
    

    widget_advanced_params = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Parameters"),
                    dbc.CardBody(
                        className='no-padding',
                        children=[
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
                                style_cell={"whiteSpace": "pre-line"}
                            ),
                            html.Div(id='table-params-dropdown-container'),
                        ]
                    )
                ]
            )
        ]
    )

    fuels = scenarioInputDefault['fuels']
    fuels_data = [dict(fuel=fuel,
                       desc=fuels[fuel]['desc'],
                       colour=fuels[fuel]['colour'],
                       type=fuels[fuel]['type'],
                       blue_type=fuels[fuel]['blue_type'] if 'blue_type' in fuels[fuel] else None,
                       include_capex=fuels[fuel]['include_capex'] if 'include_capex' in fuels[fuel] else None,
                       elecsrc=fuels[fuel]['elecsrc'] if 'elecsrc' in fuels[fuel] else None
                       ) for fuel in fuels]

    widget_advanced_fuels = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Defined fuels"),
                    dbc.CardBody(
                        className='no-padding',
                        children=[
                            dash_table.DataTable(
                                id='advanced-fuels',
                                columns=[
                                    {'id': 'fuel', 'name': 'Fuel ID'},
                                    {'id': 'desc', 'name': 'Fuel name'},
                                    {'id': 'colour', 'name': 'Colour'},
                                    {'id': 'type', 'name': 'Fuel type', 'presentation': 'dropdown'},
                                    {'id': 'blue_type', 'name': 'Blue type', 'presentation': 'dropdown'},
                                    {'id': 'include_capex', 'name': 'Include CAPEX', 'presentation': 'dropdown'},
                                    {'id': 'elecsrc', 'name': 'Electricity source', 'presentation': 'dropdown'},
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
                                    'blue_type': {
                                        'options': [
                                            {'value': 'smr', 'label': 'SMR only'},
                                            {'value': 'smr+lcrccs', 'label': 'SMR+LCRCCS'},
                                            {'value': 'smr+hcrccs', 'label': 'SMR+HCRCCS'},
                                            {'value': 'atr+hcrccs', 'label': 'ATR+HCRCCS'},
                                        ]
                                    },
                                    'include_capex': {
                                        'options': [
                                            {'value': True, 'label': 'True'},
                                            {'value': False, 'label': 'False'},
                                        ]
                                    },
                                    'elecsrc': {
                                        'options': [
                                            {'value': 'hydro', 'label': 'Hydro power'},
                                            {'value': 'wind', 'label': 'Wind power onshore'},
                                            {'value': 'solar', 'label': 'Solar PV'},
                                            {'value': 'custom', 'label': 'Use custom numbers'},
                                            {'value': 'mix', 'label': 'EU electricity mix'},
                                        ]
                                    }
                                }
                            ),
                            html.Div(id='table-fuels-dropdown-container'),
                        ]
                    )
                ]
            )
        ]
    )

    return widget_advanced_options, widget_advanced_params, widget_advanced_fuels
