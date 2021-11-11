from dash import dcc, html
import dash_bootstrap_components as dbc

from src.app.elements.header import getHeader
from src.app.elements.plot_settings_modal import getPlotSettingsModal
from src.app.elements.results import getResultsWidgets
from src.app.elements.simple import getSimpleWidgets
from src.app.elements.advanced import getAdvancedWidgets
from src.app.elements.plots import getPlots


def setLayout(app, scenarioInputDefault):
    header = getHeader(app)

    # simple config widgets
    widget_simple_options, widget_simple_green, widget_simple_blue = getSimpleWidgets(scenarioInputDefault)

    # advanced scenario config
    widget_advanced_options, widget_advanced_params, widget_advanced_fuels = getAdvancedWidgets(scenarioInputDefault)

    # results
    widget_results = getResultsWidgets()

    # plots
    fig1, fig2, fig3, fig4, fig5, fig6 = getPlots()

    # plot settings modal
    plot_settings_modal = getPlotSettingsModal()

    # explanation
    explanation = dbc.Col(
        [
            dbc.Card(
                id="description-card",
                children=[
                    dbc.CardHeader("Explanation"),
                    dbc.CardBody(
                        [
                            html.P(
                                "These graphs show analysis of the competition between blue and green hydrogen. They are also used in publication XYZ."
                                "You can adjust the numbers and see how things change. Enjoy. :)"
                            ),
                        ]
                    ),
                ],
            )
        ],
        md=12,
    )

    # define app layout
    app.layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    dbc.Row(explanation),
                    dbc.Row(
                        dbc.Col(
                            dcc.Tabs(id='control-tabs', value='simple', children=[
                                    dcc.Tab(
                                        label='Simple scenario config',
                                        value='simple',
                                        children=[
                                            dbc.Container(
                                                id='controls-container-simple',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(widget_simple_options, md=2),
                                                            dbc.Col(widget_simple_green, md=5),
                                                            dbc.Col(widget_simple_blue, md=5),
                                                        ],
                                                    ),
                                                    dbc.Row(children=[
                                                        dbc.Button(id='simple-update', n_clicks=0, children='Generate Results + Plot', className='scenario-buttons'),
                                                        dbc.Button(id='simple-download-config', n_clicks=0, children='Download Config', className='scenario-buttons')
                                                    ]),
                                                ]
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Advanced scenario config',
                                        value='advanced',
                                        children=[
                                            dbc.Container(
                                                id='controls-container-advanced',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(widget_advanced_options, md=2),
                                                            dbc.Col(widget_advanced_fuels, md=10)
                                                        ],
                                                    ),
                                                    dbc.Row(
                                                        children=[dbc.Col(widget_advanced_params, md=12)],
                                                    ),
                                                    dbc.Row(children=[
                                                        dbc.Button(id='advanced-update', n_clicks=0, children='Generate Results + Plot', className='scenario-buttons'),
                                                        dbc.Button(id='advanced-download-config', n_clicks=0, children='Download Config', className='scenario-buttons')
                                                    ]),
                                                ]
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Results',
                                        value='results',
                                        children=[
                                            dbc.Container(
                                                children=[
                                                    dbc.Row(widget_results),
                                                    dbc.Row(children=[
                                                            dbc.Button(id='results-replot', n_clicks=0, children='Replot data', className='scenario-buttons'),
                                                            html.Form(
                                                                action='/download/data.xlsx',
                                                                method='get',
                                                                children=[
                                                                    dbc.Button(id='results-download', type='submit', children='Download data', className='scenario-buttons')
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ],
                                    )
                                ]
                            ),
                            md = 12
                        )
                    ),
                    dbc.Row(
                        children=[dbc.Col(fig1, md=7), dbc.Col(fig2, md=5)],
                    ),
                    dbc.Row(
                        children=[dbc.Col(fig3, md=8), dbc.Col(fig5, md=4)],
                    ),
                    dbc.Row(
                        children=[dbc.Col(fig4, md=6), dbc.Col(fig6, md=6)],
                    ),
                ],
                fluid=True,
            ),
            plot_settings_modal,
            dcc.Store(id='saved-plot-data', storage_type='session'),
            dcc.Store(id='plotting-config', storage_type='session'),
            dcc.Download(id='download-config-yaml'),
            dcc.Download(id='download-results-xlsx'),
        ]
    )