import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go


def plotFig2(fuelsData: pd.DataFrame, fuelSpecs: dict, FSCPData: pd.DataFrame, refFuel: str = 'natural gas',
             refYear: int = 2020, showFuels = None, scenario_name = "", export_img: bool = True):
    # load config setting from YAML file
    config = {**fuelSpecs, **__getPlottingConfig()}

    # select which lines to plot based on function argument
    plotData = __selectPlotData(fuelsData, refFuel, showFuels)

    # select which FSCPs to plot based on function argument
    plotFSCP = __selectPlotFSCPs(FSCPData, refFuel, showFuels)

    # produce figure
    fig = __produceFigure(plotData, plotFSCP, refFuel, refYear, showFuels, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig2" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __getPlottingConfig():
    configThis = yaml.load(open('input/plotting/config_fig2.yml', 'r').read(), Loader=yaml.FullLoader)
    return configThis


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
    traces, cost_ref = __addFSCPTraces(refData, config)
    for trace in traces:
        fig.add_trace(trace)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['ci'],   range=[0.0, config['plotting']['ci_max']*1000]),
                      yaxis=dict(title=config['labels']['cost'], range=[cost_ref, config['plotting']['cost_max']]))

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
        traces.append(go.Scatter(x=thisData.ci*1000, y=thisData.cost,
            error_x=dict(type='data', array=thisData.ci_u*1000), error_y=dict(type='data', array=thisData.cost_u),
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

    traces.append(go.Heatmap(x=ci_samples*1000, y=cost_samples, z=fscp,
                             zsmooth='best', showscale=True, hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#c6dbef'],
                                 [1.0, '#f7bba1'],
                             ],
                             colorbar=dict(
                                 x=1.0,
                                 y=0.25,
                                 len=0.5,
                                 title='FSCP',
                                 titleside='top',
                             )))

    traces.append(go.Contour(x=ci_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=False,
                                 start=50,
                                 end=2000,
                                 size=50,
                             )))

    traces.append(go.Contour(x=ci_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             line=dict(width=1.5),
                             contours=dict(
                                 showlabels=True,
                                 labelfont=dict(
                                     size=10,
                                     color='black',
                                 ),
                                 size=100,
                                 start=100,
                                 end=600,
                             )))

    traces.append(go.Contour(x=ci_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             line=dict(width=1.5),
                             contours=dict(
                                 showlabels=True,
                                 labelfont=dict(
                                     size=10,
                                     color='black',
                                 ),
                                 size=250,
                                 start=750,
                                 end=1000,
                             )))

    traces.append(go.Contour(x=ci_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             line=dict(width=1.5),
                             contours=dict(
                                 showlabels=True,
                                 labelfont=dict(
                                     size=10,
                                     color='black',
                                 ),
                                 size=300,
                                 start=1200,
                                 end=1500,
                             )))

    return traces, cost_ref
