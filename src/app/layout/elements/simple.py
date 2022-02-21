from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from src.app.callbacks.simple_params import getSimpleParamsTable


def getElementSimpleControlsCard():
    return html.Div(
        id="simple-controls-card",
        children=[
            html.Div(
                [
                    dbc.Label(
                        "Global Warming Potential (GWP) reference time scale:",
                        html_for="simple-gwp",
                    ),
                    dcc.RadioItems(
                        id="simple-gwp",
                        options=[dict(value='gwp100', label='GWP100'), dict(value='gwp20', label='GWP20')],
                        value='gwp100',
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                [
                    dbc.Label(
                        "Most important parameters and assumptions:",
                        html_for="simple-important-params",
                    ),
                    dash_table.DataTable(
                        id="simple-important-params",
                        columns=[
                            {'id': 'name', 'name': 'Name', 'editable': False,},
                            {'id': 'desc', 'name': 'Parameter', 'editable': False,},
                            {'id': 'unit', 'name': 'Unit', 'editable': False,},
                            {'id': 'val_2025', 'name': 'Value 2025'},
                            {'id': 'val_2050', 'name': 'Value 2050'},
                        ],
                        data=getSimpleParamsTable(),
                        editable=True,
                        style_cell_conditional=[{
                            'if': {'column_id': 'name'},
                            'display': 'none',
                        }],
                    ),
                ],
                className='card-element',
            ),
            html.Div(
                children=html.Button(id='simple-update', n_clicks=0, children='Update', className='scenario-buttons'),
                className='card-element',
            ),
        ],
        className='side-card elements-card',
    )
