import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data.calc_fuels import calcFuelData
from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig8(fuelSpecs: dict, scenario: dict, fullParams: pd.DataFrame,
             config: dict, export_img: bool = True):
    # obtain data
    levelisedFuelData, _ = calcFuelData(scenario['options']['times'], fullParams, scenario['fuels'], scenario['options']['gwp'], levelised=True)

    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = levelisedFuelData.query('fuel in @fuels & year in @years')

    # add names
    plotData.insert(1, 'name', len(plotData)*[''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = f"{fuelSpecs['names'][row['fuel']]} {row['year']}"

    # produce figure
    fig = __produceFigure(plotData, config)

    # styling figure
    __styling(fig)

    # write figure to image file
    if export_img:
        w_mm = 88.0
        h_mm = 61.0

        fs_sm = getFontSize(5.0)
        fs_lg = getFontSize(7.0)

        fig.update_layout(font_size=fs_sm)
        fig.update_annotations(font_size=fs_lg)
        fig.update_xaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)
        fig.update_yaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)

        fig.write_image("output/fig8.png", **getImageSize(w_mm, h_mm))

    return fig


def __produceFigure(plotData: pd.DataFrame, config: dict):
    # create figure
    fig = px.bar(plotData,
        x='name',
        y=['ci__base',
           'ci__mleakage',
           'ci__elec',],
        color_discrete_map=config['colours'],
    )

    # make adjustments
    for trace in fig.data:
        trace['name'] = config['labels'][trace['name']]
        trace['y'] *= 1000.0
        trace['hovertemplate'] = f"<b>{trace['name']}</b><br>{config['yaxislabel']}: %{{y}}<br>For fuel %{{x}}<extra></extra>"

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=''),
                      yaxis=dict(title=config['yaxislabel']),
                      legend_title='')

    return fig


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )


    # update axis styling
    for axis in ['xaxis', 'yaxis']:
        update = {axis: dict(
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            zeroline=False,
            mirror=True,
            ticks='outside',
        )}
        fig.update_layout(**update)


    # update figure background colour and font colour and type
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 1.0)',
        plot_bgcolor='rgba(255, 255, 255, 0.0)',
        font_color='black',
        font_family='Helvetica',
    )
