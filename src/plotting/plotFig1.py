import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb


def plotFig1(fuelsData: pd.DataFrame, fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, scenario_name = "", export_img: bool = True):
    # load config setting from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotData, linesCols = __selectPlotData(fuelsData, config['showFuels'])

    # select which FSCPs to plot based on function argument
    plotFSCP, FSCPsCols = __selectPlotFSCPs(FSCPData, config['showFSCPs'])

    # produce figure
    fig = __produceFigure(plotData, linesCols, plotFSCP, FSCPsCols, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig1" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __selectPlotData(fuelsData: pd.DataFrame, showFuels: dict = None):
    linesCols = {}

    if showFuels is None:
        plotData = fuelsData.query("year == 2020")
    else:
        plotData = pd.DataFrame(columns=fuelsData.keys())
        for cols, year, fuel in showFuels:
            addFuel = fuelsData.query("year == {} & fuel == '{}'".format(year, fuel)).reset_index(drop=True)
            addFuel.index += len(plotData)
            linesCols[len(plotData)] = cols
            plotData = pd.concat([plotData, addFuel])

    return plotData, linesCols


def __selectPlotFSCPs(FSCPData: pd.DataFrame, showFSCPs: dict = None):
    FSCPsCols = {}

    if showFSCPs is None:
        plotFSCP = FSCPData.query("year_x==2020 & year_y==2020")
    else:
        plotFSCP = pd.DataFrame(columns=FSCPData.keys())
        for cols, year_x, fuel_x, year_y, fuel_y in showFSCPs:
            addFSCP = FSCPData.query("year_x=={} & fuel_x=='{}' & year_y=={} & fuel_y=='{}'".format(year_x, fuel_x, year_y, fuel_y))
            addFSCP.index += len(plotFSCP)
            FSCPsCols[len(plotFSCP)] = cols
            plotFSCP = pd.concat([plotFSCP, addFSCP], ignore_index = True)

    return plotFSCP, FSCPsCols


def __produceFigure(plotData: pd.DataFrame, linesCols: dict, plotFSCP: pd.DataFrame, FSCPsCols: dict, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=config['plotting']['numb_cols'],
                        shared_yaxes=True,
                        horizontal_spacing=0.05)

    # add line traces
    traces = __addLineTraces(plotData, config)
    for id, trace in traces:
        for j, col in enumerate(linesCols[id]):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=col)

    # add FSCP traces
    traces = __addFSCPTraces(plotFSCP, config)
    for id, trace in traces:
        for j, col in enumerate(FSCPsCols[id]):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=col)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['CP'], range=[0.0, config['plotting']['carb_price_max']]),
                      xaxis2=dict(title=config['labels']['CP'], range=[0.0, config['plotting']['carb_price_max']]),
                      yaxis=dict(title=config['labels']['total_cost'], range=[-0.05*config['plotting']['fuel_cost_max'], config['plotting']['fuel_cost_max']]))

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
        y = row.cost + row.ci * x
        y_u = np.sqrt(row.cost_u**2 + row.ci_u**2 * x**2)

        # fuel line
        traces.append((index, go.Scatter(x=x, y=y,
            name=f"{name} ({year})",
            legendgroup=f"{fuel}_{year}",
            mode="lines",
            line=dict(color=col, width=2, dash='dash' if occurrence[fuel]>1 else 'solid'),
            hovertemplate=f"<b>{name}</b><br>Carbon price: %{{x:.2f}}<br>Total cost: %{{y:.2f}}<extra></extra>")))

        # fuel uncertainty
        traces.append((index, go.Scatter(
            name='Uncertainty Range',
            legendgroup=f"{fuel}_{year}",
            x=np.concatenate((x, x[::-1])),
            y=np.concatenate((y+y_u, (y-y_u)[::-1])),
            mode='lines',
            marker=dict(color=col),
            fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(col), .1)),
            fill='toself',
            line=dict(width=.3),
            showlegend=False,
            hoverinfo="none"
        )))

    return traces


def __addFSCPTraces(plotFSCP: pd.DataFrame, config: dict):
    traces = []

    for index, row in plotFSCP.iterrows():
        name = f"Switching from <b>{config['names'][row.fuel_x]}</b><br>to <b>{config['names'][row.fuel_y]}</b>"

        # circle at intersection
        traces.append((index, go.Scatter(x=(row.fscp,), y=(row.fscp_tc,), error_x=dict(type='data', array=(row.fscp_u,), thickness=0.0),
                                 mode="markers",
                                 marker=dict(symbol='circle-open', size=12, line={'width': 2}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

        # dashed line to x-axis
        traces.append((index, go.Scatter(x=(row.fscp, row.fscp), y = (0, row.fscp_tc),
                                 mode="lines",
                                 line=dict(color='Black', width=1, dash='dot'),
                                 showlegend=False, hoverinfo='none',)))

        # error bar near x-axis
        traces.append((index, go.Scatter(x=(row.fscp,), y = (0,), error_x=dict(type='data', array=(row.fscp_u,)),
                                 marker=dict(symbol=34, size=5, line={'width': 2}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

    return traces
