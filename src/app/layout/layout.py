from dash import dcc, html

from src.app.layout.elements.advanced import getElementAdvancedControlsCardLeft, getElementAdvancedControlsCardRight
from src.app.layout.modals.advanced_modal import getModalUpdateAdvancedTable
from src.app.layout.modals.plot_settings_modal import getModalPlotConfig
from src.app.layout.elements.figures import getFigures
from src.app.layout.elements.results import getElementResultsCard
from src.app.layout.elements.simple import getElementSimpleControlsCard
from src.app.layout.elements.summary import getElementSummaryCard
from src.config_load import plotting_cfg


def getLayout(logo_url: str):
    return html.Div(
        id='app-container',

        # banner
        children=[
            html.Div(
                id='banner',
                className='banner',
                children=[
                    html.A(
                        html.Img(src=logo_url),
                        href='https://www.pik-potsdam.de/'
                    ),
                    html.Div(
                        html.B('Cost competitiveness of blue and green H₂'),
                        className='app-title',
                    ),
                    html.Div(
                        dcc.Link(
                            'Simple',
                            href='/',
                            className='mainlink',
                        ),
                        className='app-modes',
                    ),
                    html.Div(
                        dcc.Link(
                            'Advanced',
                            href='/advanced',
                            className='mainlink',
                        ),
                        className='app-modes',
                    ),
                ],
            ),

            # left column
            html.Div(
                id='left-column',
                className='four columns',
                children=[getElementSummaryCard(), getElementSimpleControlsCard(), getElementAdvancedControlsCardLeft()]
            ),

            # right column
            html.Div(
                id='right-column',
                className='eight columns',
                children=[getElementAdvancedControlsCardRight()]+getFigures()+[getElementResultsCard()],
            ),

            # modals
            getModalPlotConfig(),
            getModalUpdateAdvancedTable(),

            # dcc locations, stores, and downloads
            dcc.Location(id='url', refresh=False),
            dcc.Store(id='saved-plot-data', storage_type='session'),
            dcc.Store(id='plotting-config', storage_type='session', data=plotting_cfg),
            dcc.Download(id='download-config-yaml'),
            dcc.Download(id='download-results-xlsx'),
        ],
    )
