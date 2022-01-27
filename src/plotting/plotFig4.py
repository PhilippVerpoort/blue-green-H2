from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig4(fuelSpecs: dict, fuelsData: pd.DataFrame, fuelsDataSteel: pd.DataFrame,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # Select which lines to plot based on function argument and
    plotDataLeft, refDataLeft = __selectPlotData(fuelsData, config['refFuelLeft'], config['refYearLeft'], config['showFuels'])
    plotDataRight, refDataRight = __selectPlotData(fuelsDataSteel, config['refFuelRight'], config['refYearRight'], config['showFuels'])

    # produce figure
    fig = __produceFigure(plotDataLeft, refDataLeft, plotDataRight, refDataRight, config['showFuels'], config)

    # write figure to image file
    if export_img:
        w_mm = 180.0
        h_mm = 81.0

        fs_sm = getFontSize(5.0)
        fs_lg = getFontSize(7.0)

        fig.update_layout(font_size=fs_sm)
        fig.update_annotations(font_size=fs_sm)
        for annotation in fig['layout']['annotations'][:len(config['subplot_title_positions'])]:
            annotation['font']['size'] = fs_lg
        fig.update_xaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)
        fig.update_yaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)

        fig.write_image("output/fig4.png", **getImageSize(w_mm, h_mm))

    return fig


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, refYear: int, showFuels: list):
    plotData = fuelsData.query("fuel in @showFuels")
    refData = fuelsData.query(f"fuel=='{refFuel}' & year=={refYear}").iloc[0]

    return plotData, refData


def __produceFigure(plotDataLeft: pd.DataFrame, refDataLeft: pd.Series,
                    plotDataRight: pd.DataFrame, refDataRight: pd.Series,
                    showFuels: list, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=2,
                        subplot_titles=ascii_lowercase)


    # add line traces
    traces = __addLineTraces(plotDataLeft, showFuels, config)
    for trace in traces:
        fig.add_trace(trace, row=1, col=1)


    # add FSCP traces
    thickLines = [
        {'size': 100, 'start': 100, 'end': 600},
        {'size': 250, 'start': 750, 'end': 1000},
        {'size': 300, 'start': 1200, 'end': 1500},
    ]

    plotConf = (config['plotting']['ghgi_max_left'], config['plotting']['cost_max_left'], config['plotting']['n_samples'])
    traces = __addFSCPTraces(refDataLeft, thickLines, plotConf)
    for trace in traces:
        fig.add_trace(trace, row=1, col=1)
    #fig.add_hline(refDataLeft.cost, line_width=4, line_dash="dash", line_color='black', row=1, col=1)


    # add line traces
    traces = __addLineTraces(plotDataRight, showFuels, config)
    for trace in traces:
        trace.showlegend = False
        fig.add_trace(trace, row=1, col=2)


    # add FSCP traces
    thickLines = [
        {'size': 50, 'start': 50, 'end': 200},
    ]

    plotConf = (config['plotting']['ghgi_max_right'], config['plotting']['cost_max_right'], config['plotting']['n_samples'])
    traces = __addFSCPTraces(refDataRight, thickLines, plotConf)
    for trace in traces:
        fig.add_trace(trace, row=1, col=2)
    #fig.add_hline(refDataRight.cost, line_width=4, line_dash="dash", line_color='black', row=1, col=2)


    # set plotting ranges
    shift = 0.1
    y1low = refDataLeft.cost-shift*(config['plotting']['cost_max_left']-refDataLeft.cost)
    y2low = refDataRight.cost-shift*(config['plotting']['cost_max_right']-refDataRight.cost)
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['ghgiLeft'],
            range=[0.0, config['plotting']['ghgi_max_left']*1000]
        ),
        yaxis=dict(
            title=config['labels']['costLeft'],
            range=[y1low, config['plotting']['cost_max_left']]
        ),
        xaxis2=dict(
            title=config['labels']['ghgiRight'],
            range=[0.0, config['plotting']['ghgi_max_right']*1000]
        ),
        yaxis2=dict(
            title=config['labels']['costRight'],
            range=[y2low, config['plotting']['cost_max_right']]
        ),
    )


    # add annotations
    annotationStylingA = dict(xanchor='right', yanchor='bottom', showarrow=False, bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')
    fig.add_annotation(x=0.99*config['plotting']['ghgi_max_left']*1000,
                       y=y1low+0.01*(config['plotting']['cost_max_left']-refDataLeft.cost),
                       xref="x", yref="y", text='Heating (H2 vs. Natural Gas)', **annotationStylingA)
    fig.add_annotation(x=0.99*config['plotting']['ghgi_max_right']*1000,
                       y=y2low+0.01*(config['plotting']['cost_max_right']-refDataRight.cost),
                       xref="x2", yref="y2", text='Primary Steel Production (H2-DRI-EAF vs. Blast Furnace)', **annotationStylingA)

    annotationStylingB = dict(xanchor='left', yanchor='top', showarrow=False)
    fig.add_annotation(x=0.01*config['plotting']['ghgi_max_left']*1000,
                       y=refDataLeft.cost,
                       xref="x", yref="y", text='Price of natural gas', **annotationStylingB)
    fig.add_annotation(x=0.01*config['plotting']['ghgi_max_right']*1000,
                       y=refDataRight.cost,
                       xref="x2", yref="y2", text='Direct cost of conventional steel (BF/BOF)', **annotationStylingB)


    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.555,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )


    # update axis styling
    for axis in ['xaxis', 'yaxis', 'xaxis2', 'yaxis2']:
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


    # move title annotations
    for i, annotation in enumerate(fig['layout']['annotations'][:len(config['subplot_title_positions'])]):
        x_pos, y_pos = config['subplot_title_positions'][i]
        annotation['xanchor'] = 'left'
        annotation['yanchor'] = 'top'
        annotation['xref'] = 'paper'
        annotation['yref'] = 'paper'

        annotation['x'] = x_pos
        annotation['y'] = y_pos

        annotation['text'] = "<b>{0}</b>".format(annotation['text'])


    return fig


def __addLineTraces(plotData: pd.DataFrame, showFuels: list, config: dict):
    traces = []

    for fuel in showFuels:
        # line properties
        name = config['names'][fuel]
        col = config['colours'][fuel]
        dashed = fuel == 'green pure RE'

        # data
        thisData = plotData.query(f"fuel=='{fuel}'")
        thisData = thisData.query(f"year==[2025,2030,2040,2050]")

        # fuel line
        traces.append(go.Scatter(x=thisData.ghgi*1000, y=thisData.cost,
            error_x=dict(type='data', array=thisData.ghgi_uu*1000, arrayminus=thisData.ghgi_ul*1000, thickness=2),
            error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=2),
            text=thisData.year,
            textposition='top left',
            textfont=dict(color=col),
            name=name,
            legendgroup=fuel,
            showlegend=not dashed,
            mode="markers+lines+text",
            line=dict(color=col, width=3, dash='dash' if dashed else 'solid'),
            marker_size=10,
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity: %{{x:.2f}}<br>Direct cost: %{{y:.2f}}<extra></extra>"))

    return traces


def __addFSCPTraces(refData: pd.Series, thickLines: list, plotConf: tuple):
    traces = []

    ghgi_max, cost_max, n_samples = plotConf

    ghgi_samples = np.linspace(0.0, ghgi_max, n_samples)
    cost_samples = np.linspace(0.0, cost_max, n_samples)
    ghgi_v, cost_v = np.meshgrid(ghgi_samples, cost_samples)

    ghgi_ref = refData.ghgi
    cost_ref = refData.cost

    fscp = (cost_v - cost_ref)/(ghgi_ref - ghgi_v)

    # heatmap
    tickvals = [100*i for i in range(6)]
    ticktext = [str(v) for v in tickvals]
    ticktext[-1] = '> 500'
    traces.append(go.Heatmap(x=ghgi_samples*1000, y=cost_samples, z=fscp,
                             zsmooth='best', showscale=True, hoverinfo='skip',
                             zmin=0.0, zmax=500.0,
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
                                 tickvals=tickvals,
                                 ticktext=ticktext,
                             )))

    # thin lines every 50
    traces.append(go.Contour(x=ghgi_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=False,
                                 start=0,
                                 end=3000,
                                 size=50,
                             )))

    # zero line
    traces.append(go.Contour(x=ghgi_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=True,
                                 start=0,
                                 end=10,
                                 size=100,
                             ),
                             line=dict(width=3, dash='dash')))

    # thick lines
    for kwargs in thickLines:
        traces.append(go.Contour(
            x=ghgi_samples*1000, y=cost_samples, z=fscp,
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
                **kwargs,
            )))

    return traces
