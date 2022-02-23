from dash import dcc
import dash_bootstrap_components as dbc


def getModalPlotConfig():
    modal = dbc.Modal(
        [
            dbc.ModalHeader('Update plot config'),
            dbc.ModalBody(
                [
                    dbc.Label('Config:'),
                    dcc.Textarea(id='plot-config-modal-textfield', style={'width': '100%', 'height': 500}),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button('OK', color='primary', id='plot-config-modal-ok'),
                    dbc.Button('Cancel', id='plot-config-modal-cancel'),
                ]
            ),
        ],
        id='plot-config-modal',
    )

    return modal
