from dash import dcc
import dash_bootstrap_components as dbc


def getModalUpdateAdvancedTable():
    modal = dbc.Modal(
        [
            dbc.ModalHeader('Update parameter value'),
            dbc.ModalBody(
                [
                    dbc.Label('Value:'),
                    dcc.Textarea(id='advanced-modal-textfield', style={'width': '100%', 'height': 500}),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button('OK', color='primary', id='advanced-modal-ok'),
                    dbc.Button('Cancel', id='advanced-modal-cancel'),
                ]
            ),
        ],
        id='advanced-modal',
    )

    return modal
