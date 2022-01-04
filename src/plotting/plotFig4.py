import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig4(fuelsData: pd.DataFrame, fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotData = __selectPlotData(fuelsData, config['refFuel'], config['showFuels'])

    # select which FSCPs to plot based on function argument
    plotFSCP = __selectPlotFSCPs(FSCPData, config['refFuel'], config['showFuels'])

    # produce figure
    fig = __produceFigure(plotData, plotFSCP, config['refFuel'], config['refYear'], config['showFuels'], config)

    # write figure to image file
    if export_img:
        w_mm = 88.0
        h_mm = 81.0

        fs = getFontSize(5.0)

        fig.update_layout(font_size=fs)
        fig.update_annotations(font_size=fs)
        fig.update_xaxes(title_font_size=fs,
                         tickfont_size=fs)
        fig.update_yaxes(title_font_size=fs,
                         tickfont_size=fs)

        fig.write_image("output/fig4.png", **getImageSize(w_mm, h_mm))

    return fig


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, showFuels: list):
    fuelsList = [refFuel] + showFuels
    return fuelsData.query("fuel in @fuelsList")


def __selectPlotFSCPs(FSCPData: pd.DataFrame, refFuel: str, showFuels: list):
    return FSCPData.query(f"fuel_x in @showFuels & fuel_y=='{refFuel}'")


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
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['ci'],
            range=[0.0, config['plotting']['ci_max']*1000]
        ),
        yaxis=dict(
            title=config['labels']['cost'],
            range=[cost_ref, config['plotting']['cost_max']]
        )
    )


    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
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
            error_x=dict(type='data', array=thisData.ci_uu*1000, arrayminus=thisData.ci_ul*1000, thickness=3),
            error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=3),
            name=name,
            legendgroup=fuel,
            mode="markers+lines",
            line=dict(color=col, width=3),
            marker_size=10,
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
                                     color='black',
                                 ),
                                 size=300,
                                 start=1200,
                                 end=1500,
                             )))

    return traces, cost_ref
