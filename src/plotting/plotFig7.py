import pandas as pd
import plotly.graph_objects as go

from src.data.fuels.calc_fuels import calcFuelData
from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig7(fuelData: pd.DataFrame, config: dict, type: str = 'cost', export_img: bool = True):
    # plot data
    plotData = __obtainData(fuelData, config)

    # produce figure
    fig = __produceFigure(plotData, config, type)

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

        num = '7' if type == 'cost' else '8'
        fig.write_image(f"output/fig{num}.png", **getImageSize(w_mm, h_mm))

    return fig


def __obtainData(fuelData: pd.DataFrame, config: dict):
    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = fuelData.query('fuel in @fuels & year in @years')

    # add names
    plotData.insert(1, 'name', len(plotData) * [''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = config['names'][row['fuel']]

    # update name of green
    plotData.loc[(plotData['fuel']=='green RE') & (plotData['year']==2025), 'name'] = 'Electrolysis-RE-80%'
    plotData.loc[(plotData['fuel']=='green RE') & (plotData['year']==2050), 'name'] = 'Electrolysis-RE-100%'

    return plotData


def __produceFigure(plotData: pd.DataFrame, config: dict, type: str):
    scale = 1.0 if type == 'cost' else 1000.0

    # create figure
    fig = go.Figure()
    keys = config['labels'].keys()
    for stack in keys:
        fig.add_bar(
            x=[plotData.year, plotData.name],
            y=plotData[stack]*scale,
            marker_color=config['colours'][stack],
            name=config['labels'][stack],
            hovertemplate=f"<b>{config['labels'][stack]}</b><br>{config['yaxislabel']}: %{{y}}<br>For fuel %{{x}}<extra></extra>",
        )
    fig.update_layout(barmode='stack')

    # add error bar
    fig.add_bar(
        x=[plotData.year, plotData.name],
        y=0.00000001*plotData[list(keys)[0]],
        error_y=dict(type='data', array=plotData[f"{type}_uu"], arrayminus=plotData[f"{type}_ul"], color='black'),
        showlegend=False,
    )

    # add vertical line
    nYears = plotData['year'].nunique()
    nFuels = plotData['fuel'].nunique()
    for i in range(nYears-1):
        fig.add_vline(nFuels*(i+1)-0.5, line_width=0.5, line_color='black')
        fig.add_vline(nFuels*(i+1)-0.5, line_width=0.5, line_color='black')

    # set axes labels
    fig.update_layout(xaxis=dict(title=''),
                      yaxis=dict(title=config['yaxislabel'], range=[0.0, config['ymax']*scale]),
                      legend_title='')

    return fig


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
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
