import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.timeit import timeit


@timeit
def plot2ab(fuelData: pd.DataFrame, FSCPData: pd.DataFrame, config: dict):
    figs = {}
    for subFigName, type in [('a', 'left'), ('b', 'right')]:
        # select which lines to plot based on function argument
        plotData = __selectPlotData(fuelData, config['showFuels'][type])

        # select which FSCPs to plot based on function argument
        plotFSCP = __selectPlotFSCPs(FSCPData, config['showFSCPs'][type])

        # produce figures
        fig = __produceFigure(plotData, plotFSCP, config)

        # styling figure
        __styling(fig, subFigName)

        figs.update({f"fig2{subFigName}": fig})

    return figs


def __selectPlotData(fuelData: pd.DataFrame, showFuels: dict):
    fuelList = []

    for year, fuel in showFuels:
        newFuel = fuelData.query(f"year=={year} & fuel=='{fuel}'").reset_index(drop=True)
        fuelList.append(newFuel)

    return pd.concat(fuelList, ignore_index=True)


def __selectPlotFSCPs(FSCPData: pd.DataFrame, showFSCPs: dict):
    FSCPList = []

    for year_x, fuel_x, year_y, fuel_y, symbol in showFSCPs:
        addFSCP = FSCPData.query(f"year_x=={year_x} & fuel_x=='{fuel_x}' & year_y=={year_y} & fuel_y=='{fuel_y}'")
        addFSCP.insert(len(addFSCP.columns), 'symbol', symbol)
        FSCPList.append(addFSCP)

    return pd.concat(FSCPList, ignore_index=True)


def __produceFigure(plotData: pd.DataFrame, plotFSCP: pd.DataFrame, config: dict):
    # plot
    fig = go.Figure()


    # add line traces
    traces = __addLineTraces(plotData, config)
    for id, trace in traces:
        fig.add_trace(trace)


    # add FSCP traces
    traces = __addFSCPTraces(plotFSCP, config)
    for id, trace in traces:
        fig.add_trace(trace)


    # update axes titles and ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['CP'],
            range=[0.0, config['plotting']['carb_price_max']],
        ),
        yaxis=dict(
            title=config['labels']['total_cost'],
            range=[0.0, config['plotting']['fuel_cost_max']],
        ),
    )


    return fig


def __addLineTraces(plotData: pd.DataFrame, config: dict):
    traces = []

    occurrence = {}

    for index, row in plotData.iterrows():
        # line properties
        fuel = row['fuel']
        name = config['names'][fuel]
        col = config['colours'][fuel]
        year = row['year']

        # update line type
        if fuel not in occurrence: occurrence[fuel] = 1
        else: occurrence[fuel] += 1

        # generate plotting data
        x = np.linspace(0, config['plotting']['carb_price_max'], 120)
        y = row.cost + row.ghgi * x
        y_uu = np.sqrt(row.cost_uu**2 + row.ghgi_uu**2 * x**2)
        y_ul = np.sqrt(row.cost_ul**2 + row.ghgi_ul**2 * x**2)

        # fuel line
        traces.append((index, go.Scatter(x=x, y=y,
            name=f"{name} ({year})" if fuel!='natural gas' else 'Natural gas',
            legendgroup=f"{fuel}_{year}",
            mode="lines",
            line=dict(color=col, width=config['global']['lw_default'], dash='dash' if occurrence[fuel]>1 else 'solid'),
            hovertemplate=f"<b>{name}</b><br>Carbon price: %{{x:.2f}}<br>Total cost: %{{y:.2f}}<extra></extra>")))

        # fuel uncertainty
        if config['plotting']['uncertainty']:
            traces.append((index, go.Scatter(
                name='Uncertainty Range',
                legendgroup=f"{fuel}_{year}",
                x=np.concatenate((x, x[::-1])),
                y=np.concatenate((y+y_uu, (y-y_ul)[::-1])),
                mode='lines',
                marker=dict(color=col),
                fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(col), .1)),
                fill='toself',
                line=dict(width=config['global']['lw_ultrathin']),
                showlegend=False,
                hoverinfo="none"
            )))

    return traces


def __addFSCPTraces(plotFSCP: pd.DataFrame, config: dict):
    traces = []

    for index, row in plotFSCP.iterrows():
        name = f"Switching from <b>{config['names'][row.fuel_x]}</b><br>to <b>{config['names'][row.fuel_y]}</b>"

        # circle at intersection
        traces.append((index, go.Scatter(x=(row.fscp,), y=(row.fscp_tc,), error_x=dict(type='data', array=(row.fscp_uu,), arrayminus=(row.fscp_ul,), thickness=0.0),
                                 mode="markers",
                                 marker=dict(symbol=row.symbol, size=config['global']['highlight_marker'], line={'width': config['global']['lw_thin']}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

        # dashed line to x-axis
        traces.append((index, go.Scatter(x=(row.fscp, row.fscp), y = (0, row.fscp_tc),
                                 mode="lines",
                                 line=dict(color='Black', width=config['global']['lw_thin'], dash='dot'),
                                 showlegend=False, hoverinfo='none',)))

        # error bar near x-axis
        traces.append((index, go.Scatter(x=(row.fscp,), y = (0,),
                                 error_x=dict(type='data', array=(row.fscp_uu,), arrayminus=(row.fscp_ul,)) if config['plotting']['uncertainty'] else None,
                                 marker=dict(symbol='x-thin', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin']}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

    return traces


def __styling(fig: go.Figure, subFigName: str):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.005,
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


    # add title annotation
    fig.add_annotation(
        showarrow=False,
        text=f"<b>{subFigName}</b>",
        x=0.0,
        xanchor='left',
        xref='paper',
        y=1.15,
        yanchor='top',
        yref='paper',
    )


    # margins
    if subFigName == 'a':
        fig.update_layout(
            margin_r=0.0
        )
    elif subFigName == 'b':
        fig.update_layout(
            margin_l=0.0,
            yaxis=dict(title=None, ticks=None, showticklabels=False),
        )
