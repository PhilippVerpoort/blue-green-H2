import pandas as pd

import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.timeit import timeit


@timeit
def plotCostAndEmiOverTime(fuelData: pd.DataFrame, config: dict):
    # produce figures
    figs = {}
    for subFigName, type in [('a', 'cost'), ('b', 'ghgi')]:

        fig = __produceFigure(fuelData, config['fuelSpecs'], {**config[type], **{'global': config['global']}}, type)

        # styling figure
        __styling(fig)

        figs.update({f"fig8{subFigName}": fig})

    return figs


def __produceFigure(plotData: pd.DataFrame, fuelSpecs: dict, subConfig: dict, type: str):
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


    for cID, corridor in subConfig['showCorridors'].items():
        cCases = corridor['cases']
        cLabel = corridor['label']
        cColour = fuelSpecs[cCases[0]]['colour']
        print(cLabel, cColour)

        thisData = plotData.query('fuel in @cCases').reset_index(drop=True)

        thisData['upper'] = thisData[type] + thisData[type + '_uu']
        thisData['lower'] = thisData[type] - thisData[type + '_ul']

        thisData_max = thisData.loc[thisData.groupby('year')['upper'].idxmax()]
        thisData_min = thisData.loc[thisData.groupby('year')['lower'].idxmin()]

        trace = go.Scatter(
            # The minimum (or maximum) line needs to be added before the below area plot can be applied.
            x=thisData_min.year,
            y=thisData_min['upper']*scale,
            legendgroup=cID,
            mode='lines',
            line=dict(color=cColour, width=subConfig['global']['lw_default']),
            showlegend=False
        )
        fig.add_trace(trace)

        corridor = go.Scatter(
            x=thisData_max.year,
            y=thisData_max['lower']*scale,
            fill='tonexty',  # fill area between trace0 and trace1
            mode='lines',
            name=cLabel,
            legendgroup=cID,
            line=dict(color=cColour, width=subConfig['global']['lw_default']),
            showlegend=True,
        )
        fig.add_trace(corridor)


    # add label inside plot
    fig.add_annotation(
        text=subConfig['label'],
        xanchor='left',
        xref='x domain',
        x=0.01,
        yanchor='bottom',
        yref='y domain',
        y=0.015,
        showarrow=False,
        bordercolor='black',
        borderwidth=2,
        borderpad=3,
        bgcolor='white',
    )


    # set axes labels
    fig.update_layout(
        xaxis=dict(title='', zeroline=True),
        yaxis=dict(title=subConfig['yaxislabel'], zeroline=True, range=[0, subConfig['ymax']*scale]),
        legend_title='',
    )
    fig.update_yaxes(rangemode= "tozero")

    return fig


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=1.00,
            xanchor='right',
            x=1.00,
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
