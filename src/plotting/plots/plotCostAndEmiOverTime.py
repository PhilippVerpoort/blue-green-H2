from string import ascii_lowercase #TODO probably not all of this is needed for Falko's new plot

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.timeit import timeit

@timeit
def plotCostAndEmiOverTime(fuelData: pd.DataFrame, config: dict):
    #TODO, ADD HERE, Philipp? select which lines to plot already based on function argument?

    # # plot data
    plotData = __obtainData(fuelData, config)

    # produce figures
    figs = {}
    for subFigName, type in [('a', 'cost'), ('b', 'ghgi')]:

        fig = __produceFigure(plotData, {**config[type], **{'global': config['global']}, **{'colours': config['colours']}}, type)

        # styling figure
        __styling(fig, subFigName)

        figs.update({f"fig8{subFigName}": fig})

    return figs


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

    has_legend = []
    newnames = {'NG': 'Natural Gas', 'SMR56': 'Blue H<sub>2</sub> (SMR56)', 'ATR93': 'Blue H<sub>2</sub> (ATR93)', 'ELEC': 'Green H<sub>2</sub>'}  # legend labels
    title_names = {'cost': 'Direct costs', 'ghgi': 'Emission intensity'}  # titles
    for fuel in plotData.fuel.unique():
        thisData = plotData.query(f"fuel=='{fuel}'")

        tech = fuel.split("-")[0]

        trace = go.Scatter(
            x=thisData.year,
            y=thisData[type],
            name= newnames[tech], #fuel,
            legendgroup= tech, #fuel,
            mode="lines",
            line=dict(color=plotConfig["colours"][fuel], width=plotConfig['global']['lw_default']),
            showlegend=newnames[tech] not in has_legend,
            opacity = 1
        )
       # fig.add_trace(trace)
        if newnames[tech] not in has_legend:
            has_legend.append(newnames[tech])
    n = 0

    for tech in ['ELEC','ATR93','SMR56','NG']:
        n = n + 1
        #tech = fuel.split("-")[0]
        thisData = plotData.query(f"fuel.str.contains('{tech}')", engine='python')
        thisData_max = thisData.loc[thisData.groupby("year")[type].idxmax()]
        thisData_min = thisData.loc[thisData.groupby("year")[type].idxmin()]
        fuel = thisData_min.fuel.unique()[0]

        trace = go.Scatter(# The minimum (or maximum) line needs to be added before the below area plot can be applied.
            x=thisData_min.year,
            y=thisData_min[type],
           # name=tech,  # fuel,
          #  legendgroup=tech,  # fuel,
          mode="lines",
            line=dict(color=plotConfig["colours"][fuel]),
            opacity=1,
            #line=dict(color=plotConfig["colours"][fuel], width=plotConfig['global']['lw_default']),
            showlegend= False
        )
        fig.add_trace(trace)

        corridor = go.Scatter(
            x=thisData_max.year,
            y=thisData_max[type],
            fill='tonexty',  # fill area between trace0 and trace1
            mode='lines', line_color=plotConfig["colours"][fuel],
            name=newnames[tech],  # fuel,
            legendgroup=tech,  # fuel,
            # line=dict(color=plotConfig["colours"][fuel], width=plotConfig['global']['lw_default']),
            showlegend=True,
        )
        fig.add_trace(corridor)

    # set axes labels
    fig.update_layout(xaxis=dict(title='', zeroline=True),
                      yaxis=dict(title=plotConfig['yaxislabel'],zeroline=True),
                      legend_title='',
                      title=title_names[type])
    fig.update_yaxes(rangemode= "tozero")

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


def __obtainData(fuelData: pd.DataFrame, config: dict):
    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = fuelData.query('fuel in @fuels & year in @years')

    # add names
    plotData.insert(1, 'name', len(plotData) * [''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = config['names'][row['fuel']]

    return plotData





