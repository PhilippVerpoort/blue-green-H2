import pandas as pd
import plotly.graph_objects as go

from src.data.calc_fuels import calcFuelData
from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig7(fuelSpecs: dict, scenario: dict, fullParams: pd.DataFrame,
             config: dict, export_img: bool = True):
    # obtain data
    plotData = __obtainData(fuelSpecs, scenario, fullParams, config)

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

        fig.write_image('output/fig7.png', **getImageSize(w_mm, h_mm))

    return fig


def __obtainData(fuelSpecs: dict, scenario: dict, fullParams: pd.DataFrame, config: dict):
    levelisedFuelData, _ = calcFuelData(scenario['options']['times'], fullParams, scenario['fuels'],
                                        scenario['options']['gwp'], levelised=True)

    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = levelisedFuelData.query('fuel in @fuels & year in @years')

    # add names
    plotData.insert(1, 'name', len(plotData) * [''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = fuelSpecs['names'][row['fuel']]

    # update name of green
    plotData.loc[(plotData['fuel']=='green RE') & (plotData['year']==2025), 'name'] = 'Electrolysis-RE-90%'
    plotData.loc[(plotData['fuel']=='green RE') & (plotData['year']==2050), 'name'] = 'Electrolysis-RE-100%'

    return plotData


def __produceFigure(plotData: pd.DataFrame, config: dict):
    # create figure
    fig = go.Figure()
    for stack in config['labels'].keys():
        fig.add_bar(
            x=[plotData.year, plotData.name],
            y=plotData[stack],
            marker_color=config['colours'][stack],
            name=config['labels'][stack],
            hovertemplate=f"<b>{config['labels'][stack]}</b><br>{config['yaxislabel']}: %{{y}}<br>For fuel %{{x}}<extra></extra>",
        )
    fig.update_layout(barmode='stack')

    # add vertical line
    nYears = plotData['year'].nunique()
    nFuels = plotData['fuel'].nunique()
    for i in range(nYears-1):
        fig.add_vline(nFuels*(i+1)-0.5, line_width=0.5, line_color='black')
        fig.add_vline(nFuels*(i+1)-0.5, line_width=0.5, line_color='black')

    # set axes labels
    fig.update_layout(xaxis=dict(title=''),
                      yaxis=dict(title=config['yaxislabel']),
                      legend_title='')

    return fig


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=0.98,
            xanchor='right',
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
