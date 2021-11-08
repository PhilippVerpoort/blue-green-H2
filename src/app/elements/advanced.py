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
                            dbc.FormGroup(
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
                            dbc.FormGroup(
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

    fuels = scenarioInputDefault['fuels']
    fuels_data = [dict(fuel=fuel,
                       desc=fuels[fuel]['desc'],
                       type=fuels[fuel]['type'],
                       capture_rate=fuels[fuel]['capture_rate'] if 'capture_rate' in fuels[fuel] else None,
                       methane_leakage=fuels[fuel]['methane_leakage'] if 'methane_leakage' in fuels[fuel] else None,
                       include_capex=fuels[fuel]['include_capex'] if 'include_capex' in fuels[fuel] else None,
                       elecsrc=fuels[fuel]['elecsrc'] if 'elecsrc' in fuels[fuel] else None
                       ) for fuel in fuels]

    widget_advanced_fuels = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Defined fuels"),
                    dbc.CardBody(
                        children=[
                            dash_table.DataTable(
                                id='advanced-fuels',
                                columns=[{'id': 'fuel', 'name': 'Fuel ID'},
                                         {'id': 'desc', 'name': 'Fuel name'},
                                         {'id': 'type', 'name': 'Fuel type', 'presentation': 'dropdown'},
                                         {'id': 'capture_rate', 'name': 'Blue type'},
                                         {'id': 'methane_leakage', 'name': 'Methane leakage'},
                                         {'id': 'include_capex', 'name': 'Include CAPEX'},
                                         {'id': 'elecsrc', 'name': 'Electricity source'}, ],
                                data=fuels_data,
                                editable=True,
                                dropdown={
                                    'type': {
                                        'options': [
                                            {'value': 'ng', 'label': 'Natural Gas'},
                                            {'value': 'blue', 'label': 'Blue Hydrogen'},
                                            {'value': 'green', 'label': 'Green Hydrogen'},
                                        ]
                                    }
                                }
                            ),
                            html.Div(id='table-dropdown-container'),
                        ]
                    )
                ]
            )
        ]
    )

    return widget_advanced_options, widget_advanced_fuels
