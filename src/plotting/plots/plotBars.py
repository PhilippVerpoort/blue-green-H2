import pandas as pd
import plotly.graph_objects as go

from src.timeit import timeit


@timeit
def plotBars(fuelData: pd.DataFrame, config: dict):
    # plot data
    plotData = __obtainData(fuelData, config)

    # produce figures
    figs = {}
    for subFigName, type in [('a', 'cost'), ('b', 'ghgi')]:
        fig = __produceFigure(plotData, {**config[type], **{'global': config['global']}}, type)

        # styling figure
        __styling(fig, subFigName)

        figs.update({f"fig1{subFigName}": fig})

    return figs


def __obtainData(fuelData: pd.DataFrame, config: dict):
    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = fuelData.query('fuel in @fuels & year in @years')

    # add names
    plotData.insert(1, 'name', len(plotData) * [''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = config['fuelSpecs'][row['fuel']]['name']

    return plotData


def __produceFigure(plotData: pd.DataFrame, plotConfig: dict, type: str):
    scale = 1.0 if type == 'cost' else 1000.0

    # create figure
    fig = go.Figure()

    # subplot labels
    fig.add_annotation(
        showarrow=False,
        text=f"<b>{'a' if type=='cost' else 'b'}</b>",
        x=0.0,
        xanchor='left',
        xref='paper',
        y=1.2,
        yanchor='top',
        yref='paper',
    )

    # add bars
    keys = plotConfig['labels'].keys()
    for stack in keys:
        fig.add_bar(
            x=[plotData.year, plotData.fuel],
            y=plotData[stack]*scale,
            marker_color=plotConfig['colours'][stack],
            name=plotConfig['labels'][stack],
            hovertemplate=f"<b>{plotConfig['labels'][stack]}</b><br>{plotConfig['yaxislabel']}: %{{y}}<br>For fuel %{{x}}<extra></extra>",
        )
    fig.update_layout(barmode='stack')

    # add error bar
    fig.add_bar(
        x=[plotData.year, plotData.fuel],
        y=0.00000001*plotData[type],
        error_y=dict(
            type='data',
            array=plotData[f"{type}_uu"]*scale,
            arrayminus=plotData[f"{type}_ul"]*scale,
            color='black',
            thickness=plotConfig['global']['lw_thin'],
            width=plotConfig['global']['highlight_marker_sm'],
        ),
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
                      yaxis=dict(title=plotConfig['yaxislabel'], range=[0.0, plotConfig['ymax'] * scale]),
                      legend_title='')

    return fig


def __styling(fig: go.Figure, subFigName: str):
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
