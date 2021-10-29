import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go


def plotFig2(fuelsData: pd.DataFrame, FSCPData: pd.DataFrame, refFuel: str = 'natural gas', refYear: int = 2020, showFuels = None, scenario_name = ""):
    # load config setting from YAML file
    config = __getPlottingConfig()

    # select which lines to plot based on function argument
    plotData = __selectPlotData(fuelsData, refFuel, showFuels)

    # select which FSCPs to plot based on function argument
    plotFSCP = __selectPlotFSCPs(FSCPData, refFuel, showFuels)

    # produce figure
    fig = __produceFigure(plotData, plotFSCP, refFuel, refYear, showFuels, config)

    # write figure to image file
    fig.write_image("output/fig2" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __getPlottingConfig():
    configAll = yaml.load(open('input/plotting/config_all.yml', 'r').read(), Loader=yaml.FullLoader)
    configThis = yaml.load(open('input/plotting/config_fig2.yml', 'r').read(), Loader=yaml.FullLoader)
    return {**configAll, **configThis}


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, showFuels: list):
    fuelsList = [refFuel] + showFuels
    return fuelsData.query("fuel.isin(@fuelsList)")


def __selectPlotFSCPs(FSCPData: pd.DataFrame, refFuel: str, showFuels: list):
    return FSCPData.query(f"fuel_x.isin(@showFuels) & fuel_y=='{refFuel}'")


def __produceFigure(plotData: pd.DataFrame, plotFSCP: pd.DataFrame, refFuel: str, refYear: int, showFuels: list, config: dict):
    # plot
    fig = go.Figure()

    # add line traces
    traces = __addLineTraces(plotData, plotFSCP, showFuels, config)
    for trace in traces:
        fig.add_trace(trace)

    # add FSCP traces
    refData = plotData.query(f"fuel=='{refFuel}' & year=={refYear}").iloc[0]
    traces = __addFSCPTraces(refData, config)
    for trace in traces:
        fig.add_trace(trace)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['ci'],   range=[0.0, config['plotting']['ci_max']]),
                      yaxis=dict(title=config['labels']['cost'], range=[0.0, config['plotting']['cost_max']]))

    return fig


def __addLineTraces(plotData: pd.DataFrame, plotFSCP: pd.DataFrame, showFuels: list, config: dict):
    traces = []

    for fuel in showFuels:
        # line properties
        name = config['names'][fuel]
        col = config['colours'][fuel]

        # data
        thisData = plotData.query(f"fuel=='{fuel}'")

        # fuel line
        traces.append(go.Scatter(x=thisData.ci, y=thisData.cost,
            error_x=dict(type='data', array=thisData.ci_u), error_y=dict(type='data', array=thisData.cost_u),
            name=name,
            legendgroup=fuel,
            mode="markers+lines",
            line=dict(color=col, width=1),
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity: %{{x:.2f}}<br>Direct cost: %{{y:.2f}}<extra></extra>"))

    return traces


def __addFSCPTraces(refData: pd.DataFrame, config: dict):
    traces = []

    ci_samples = np.linspace(0.0, config['plotting']['ci_max'], config['plotting']['n_samples'])
    cost_samples = np.linspace(0.0, config['plotting']['cost_max'], config['plotting']['n_samples'])
    ci_v, cost_v = np.meshgrid(ci_samples, cost_samples)

    ci_ref = refData.ci
    cost_ref = refData.cost

    fscp = (cost_v - cost_ref)/(ci_ref - ci_v)

    traces.append(go.Heatmap(x=ci_samples, y=cost_samples, z=fscp,
                             zsmooth='best', showscale=False, hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#c6dbef'],
                                 [1.0, '#f7bba1'],
                             ]))

    traces.append(go.Contour(x=ci_samples, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ]))

    return traces

    nSamples = 960
    swp_samples = pd.DataFrame(data={'i': list(range(0, nSamples + 1))}).assign(j=lambda x: x.i % 31,
                                                                                k=lambda x: x.i // 31).assign(
        e=lambda x: max_emis_xaxis * x.j / 30, c=lambda x: ref_c + (max_cost_yaxis - ref_c) * x.k / 30,
        swp=lambda x: (x.c - ref_c) / (ref_e * 1.01 - x.e))

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
