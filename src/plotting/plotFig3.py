import yaml
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plotFig3(fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, scenario_name = "", export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotFSCP, FSCPsCols = __selectPlotFSCPs(FSCPData, config['showFSCPs'])

    # produce figure
    fig = __produceFigure(plotFSCP, FSCPsCols, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig3" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __selectPlotFSCPs(FSCPData: pd.DataFrame, showFSCPs: dict = None):
    FSCPsCols = [None] * len(showFSCPs)

    if showFSCPs is None:
        plotFSCP = FSCPData.query("fuel_x=='green RE' & fuel_y=='natural gas' & year_x==year_y")
    else:
        plotFSCP = pd.DataFrame(columns=(FSCPData.keys().tolist() + ['plotIndex']))
        for index, args in enumerate(showFSCPs):
            cols, fuel_x, fuel_y = args
            addFSCP = FSCPData.query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y")
            addFSCP.insert(1, 'plotIndex', len(addFSCP)*[index])
            FSCPsCols[index] = cols
            plotFSCP = pd.concat([plotFSCP, addFSCP], ignore_index=True)

    plotFSCP['year'] = plotFSCP['year_x']
    plotFSCP = plotFSCP[['fuel_x', 'fuel_y', 'year', 'fscp', 'fscp_u', 'plotIndex']]

    return plotFSCP, FSCPsCols


def __produceFigure(plotFSCP: pd.DataFrame, FSCPsCols: dict, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=config['plotting']['numb_cols'],
                        shared_yaxes=True,
                        horizontal_spacing=0.05)

    # add FSCP traces
    traces = __addFSCPTraces(plotFSCP, len(FSCPsCols), config)
    for id, trace in traces:
        for j, col in enumerate(FSCPsCols[id]):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=col)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['time'], range=[2018, 2052]),
                      xaxis2=dict(title=config['labels']['time'], range=[2018, 2052]),
                      yaxis=dict(title=config['labels']['fscp'], range=[0.0, config['plotting']['fscp_max']]))

    return fig


def __addFSCPTraces(plotData: pd.DataFrame, n_lines: int, config: dict):
    traces = []

    for index in range(n_lines):
        thisData = plotData.query(f"plotIndex=={index}").reset_index(drop=True)

        # line properties
        fuel_x = thisData.iloc[thisData.first_valid_index()]['fuel_x']
        fuel_y = thisData.iloc[0]['fuel_y']
        name = f"{config['names'][fuel_x]} to {config['names'][fuel_y]}"
        col = config['fscp_colours'][f"{fuel_x} to {fuel_y}"] if f"{fuel_x} to {fuel_y}" in config['fscp_colours'] else config['colours'][fuel_y]

        # fuel line
        traces.append((index, go.Scatter(x=thisData['year'], y=thisData['fscp'],
            error_y=dict(type='data', array=thisData['fscp_u']),
            name=name,
            legendgroup=f"{fuel_x} {fuel_y}",
            mode="lines+markers",
            line=dict(color=col, width=2),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>")))

    return traces
