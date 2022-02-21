from dash import html
from src.config_load_app import app_cfg


# description card
def getElementSummaryCard():
    return html.Div(
        id='summary-card',
        children=[
            html.H5('PIK interactive plotting app'),
            html.H3(app_cfg['title']),
            html.Div(
                id='desc',
                children=app_cfg['desc'],
            ),
            html.Div(
                id='auth',
                children=app_cfg['auth'],
            ),
            html.Div(
                id='date',
                children=f"Published on {app_cfg['date']}",
            ),
        ],
        className='side-card elements-card',
    )
