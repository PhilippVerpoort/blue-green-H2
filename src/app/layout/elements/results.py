from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


def getElementResultsCard():
    return html.Div(
        id='results-card',
        children=[
            html.Div(
                children=[
                    dbc.Label(
                        'Results',
                        html_for='table-results',
                    ),
                    dash_table.DataTable(
                        id='table-results',
                        columns=[
                            {'id': 'fuel', 'name': 'Fuel ID'},
                            {'id': 'year', 'name': 'Year'},
                            {'id': 'cost', 'name': 'Cost (EUR/MWh)'},
                            {'id': 'ghgi', 'name': 'GHG intensity (tCO2eq/MWh)'},
                        ],
                        data=[],
                        editable=True,
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                children=[
                    html.Form(
                        action='/download/data.xlsx',
                        method='get',
                        children=[
                            dbc.Button(id='results-download', type='submit', children='Download data',
                                       className='scenario-buttons')
                        ],
                        style={'float': 'left'},
                    ),
                    html.Button(id='results-replot', n_clicks=0, children='Replot using data'),
                ],
                className='card-element',
            )
        ],
        className='side-card elements-card',
        style={'display': 'none'},
    )
