from dash import html, dcc

from src.config_load import plots
from src.config_load_app import figs_cfg, app_cfg


def getFigures():
    cards = []

    for fig in app_cfg['figures']:
        plotName = next(plotName for plotName in plots if fig in plots[plotName])
        figCard = __getFigTemplate(fig, plots[plotName][fig], plotName)
        cards.append(figCard)

    return cards


def __getFigTemplate(figName: str, subFigNames: list, plotName: str):
    figCfg = figs_cfg[figName]
    width = figCfg['width'] if 'width' in figCfg else '100%'
    height = figCfg['height'] if 'height' in figCfg else '450px'
    display = False

    return html.Div(
        id=f"card-{figName}",
        className='fig-card',
        children=[
            *(
                dcc.Loading(
                    children=[
                        dcc.Graph(
                            id=subFigName,
                            style={
                                'height': height,
                                'width': width,
                                'float': 'left',
                            },
                        ),
                    ],
                    type='circle',
                    style={
                        'height': height,
                        'width': width,
                        'float': 'left',
                    },
                )
                for subFigName in subFigNames
            ),
            html.Hr(),
            html.B(f"{figCfg['name']} | {figCfg['title']}"),
            html.P(figCfg['desc']),
            (html.Div([
                    html.Hr(),
                    html.Button(id=f"{plotName}-settings", children='Config', n_clicks=0,),
                ],
                id=f"{plotName}-settings-div",
                style={'display': 'none'},
            ) if ('nosettings' not in figCfg or not figCfg['nosettings']) else None),
        ],
        style={} if display else {'display': 'none'},
    )
