import yaml
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


cons_vs_prog_params = {
    'ghgi_ng_methaneleakage': ['NG', 'BLUE'],
    'cost_green_elec': ['GREEN'],
    'cost_green_capex': ['GREEN'],
    'green_share': ['GREEN'],
    'green_ocf': ['GREEN'],
    'cost_h2transp': ['GREEN'],
}

gas_prices_params = {
    'cost_ng_price': ['NG', 'BLUE'],
}

editTablesModal = {
    'simple-important-params': ['cons', 'prog'],
    'simple-gas-prices': ['high', 'low'],
    'advanced-params': ['value'],
}


# create main control card
def main_ctrl(default_inputs: dict):
    return [html.Div(
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
                            {'id': 'name', 'name': 'Name', 'editable': False, },
                            {'id': 'desc', 'name': 'Parameter', 'editable': False, },
                            {'id': 'unit', 'name': 'Unit', 'editable': False, },
                            {'id': 'cons', 'name': 'Conservative cases'},
                            {'id': 'prog', 'name': 'Progressive cases'},
                        ],
                        data=getSimpleParamsTable(default_inputs, cons_vs_prog_params, ['cons', 'prog'], 'cons_vs_prog'),
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
                            {'id': 'name', 'name': 'Name', 'editable': False, },
                            {'id': 'desc', 'name': 'Parameter', 'editable': False, },
                            {'id': 'unit', 'name': 'Unit', 'editable': False, },
                            {'id': 'high', 'name': 'High price'},
                            {'id': 'low', 'name': 'Low price'},
                        ],
                        data=getSimpleParamsTable(default_inputs, gas_prices_params, ['high', 'low'], 'gas_prices'),
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
                        options=[
                            dict(value='gwp100', label='GWP100'),
                            dict(value='gwp20', label='GWP20'),
                        ],
                        value='gwp100',
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                children=[
                    html.Button(id='simple-update', n_clicks=0, children='GENERATE', className='scenario-buttons'),
                ],
                className='card-element',
            ),
        ],
        className='side-card',
    )]

def getSimpleParamsTable(inputs: dict, paramList: dict, casesNames: list, casesType: str):
    r = []

    paramData = inputs['params']
    fuelData = inputs['fuels']

    for parName in paramList:
        fuel = paramList[parName][0]
        r.append({
            'name': parName,
            'desc': paramData[parName]['short'] if 'short' in paramData[parName] else paramData[parName]['desc'],
            'unit': paramData[parName]['unit'],
            **{
                case: yaml.dump(
                    fuelData[fuel]['cases'][casesType][case][parName]
                    if parName in fuelData[fuel]['cases'][casesType][case] else
                    paramData[parName]['value']
                ) for case in casesNames
            },
        })

    return r
