import pandas as pd

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


def getResultsWidgets():

    widget_results = dbc.Card(
        [
            html.Div(
                children=[
                    dbc.CardHeader("Results"),
                    dbc.CardBody(
                        className='no-padding',
                        children=[
                            dash_table.DataTable(
                                id='table-results',
                                columns=[
                                    {'id': 'fuel', 'name': 'Fuel ID'},
                                    {'id': 'year', 'name': 'Year'},
                                    {'id': 'cost', 'name': 'Cost in EUR/MWh'},
                                    {'id': 'cost_u', 'name': 'Cost uncertainty'},
                                    {'id': 'ghgi', 'name': 'Carbon intensity in tCO2eq/MWh'},
                                    {'id': 'ghgi_u', 'name': 'Carbon intensity uncertainty'},
                                ],
                                data=[],
                                editable=True,
                            ),
                        ]
                    )
                ]
            )
        ],
        style={'margin-left': '1em', 'margin-right': '1em'},
    )

    return widget_results
