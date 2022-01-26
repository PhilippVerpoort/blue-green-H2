from dash import dcc
import dash_bootstrap_components as dbc


def getPlotSettingsModal():
    modal = dbc.Modal(
        [
            dbc.ModalHeader("Update plot settings"),
            dbc.ModalBody(
                [
                    dbc.Label("Settings:"),
                    dcc.Textarea(id="settings-modal-textfield", style={'width': '100%', 'height': 500}),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("OK", color="primary", id="settings-modal-ok"),
                    dbc.Button("Cancel", id="settings-modal-cancel"),
                ]
            ),
        ],
        id="settings-modal",
    )

    return modal
