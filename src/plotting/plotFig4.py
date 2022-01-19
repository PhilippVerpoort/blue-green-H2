from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.plotting.img_export_cfg import getFontSize, getImageSize
from src.config_load import steel_data


def plotFig4(fuelsData: pd.DataFrame, fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotDataLeft = __selectPlotData(fuelsData, config['refFuel'], config['showFuels'])

    # convert hydrogen data (cost and ci) into steel data
    plotDataRight = __convertDataSteel(fuelsData)

    # load reference data
    refDataLeft = plotDataLeft.query(f"fuel=='{config['refFuel']}' & year=={config['refYear']}").iloc[0]
    refDataRight = pd.Series(data={'cost': steel_data['bf_cost'], 'ci': steel_data['bf_ci']})

    # produce figure
    fig = __produceFigure(plotDataLeft, refDataLeft, plotDataRight, refDataRight, config['showFuels'], config)

    # write figure to image file
    if export_img:
        w_mm = 180.0
        h_mm = 81.0

        fs_sm = getFontSize(5.0)
        fs_lg = getFontSize(7.0)

        fig.update_layout(font_size=fs_sm)
        fig.update_annotations(font_size=fs_lg)
        fig.update_xaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)
        fig.update_yaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)

        fig.write_image("output/fig4.png", **getImageSize(w_mm, h_mm))

    return fig


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, showFuels: list):
    fuelsList = [refFuel] + showFuels
    return fuelsData.query("fuel in @fuelsList")


def __convertDataSteel(plotDataLeft: pd.DataFrame):
    plotDataRight = plotDataLeft.copy()

    plotDataRight['cost'] = plotDataRight['cost'] * steel_data['h2_demand'] + steel_data['other_cost']
    plotDataRight['cost_uu'] = plotDataRight['cost_uu'] * steel_data['h2_demand']
    plotDataRight['cost_ul'] = plotDataRight['cost_ul'] * steel_data['h2_demand']

    plotDataRight['ci'] = plotDataRight['ci'] * steel_data['h2_demand'] + steel_data['other_ci']
    plotDataRight['ci_uu'] = plotDataRight['ci_uu'] * steel_data['h2_demand']
    plotDataRight['ci_ul'] = plotDataRight['ci_ul'] * steel_data['h2_demand']

    return plotDataRight


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
    plotConf = (config['plotting']['ci_max_left'], config['plotting']['cost_max_left'], config['plotting']['n_samples'])
    traces = __addFSCPTraces(refDataLeft, plotConf)
    for trace in traces:
        fig.add_trace(trace, row=1, col=1)


    # add line traces
    traces = __addLineTraces(plotDataRight, showFuels, config)
    for trace in traces:
        trace.showlegend = False
        fig.add_trace(trace, row=1, col=2)


    # add FSCP traces
    plotConf = (config['plotting']['ci_max_right'], config['plotting']['cost_max_right'], config['plotting']['n_samples'])
    traces = __addFSCPTraces(refDataRight, plotConf)
    for trace in traces:
        fig.add_trace(trace, row=1, col=2)


    # set plotting ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['ciLeft'],
            range=[0.0, config['plotting']['ci_max_left']*1000]
        ),
        yaxis=dict(
            title=config['labels']['costLeft'],
            range=[refDataLeft.cost, config['plotting']['cost_max_left']]
        ),
        xaxis2=dict(
            title=config['labels']['ciRight'],
            range=[0.0, config['plotting']['ci_max_right']*1000]
        ),
        yaxis2=dict(
            title=config['labels']['costRight'],
            range=[refDataRight.cost, config['plotting']['cost_max_right']]
        ),
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
    for i, annotation in enumerate(fig['layout']['annotations']):
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

        # data
        thisData = plotData.query(f"fuel=='{fuel}'")
        thisData = thisData.query(f"year==[2025,2030,2040,2050]")

        # fuel line
        traces.append(go.Scatter(x=thisData.ci*1000, y=thisData.cost,
            error_x=dict(type='data', array=thisData.ci_uu*1000, arrayminus=thisData.ci_ul*1000, thickness=2),
            error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=2),
            text=thisData.year,
            textposition='top left',
            textfont=dict(color=col),
            name=name,
            legendgroup=fuel,
            mode="markers+lines+text",
            line=dict(color=col, width=3),
            marker_size=10,
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity: %{{x:.2f}}<br>Direct cost: %{{y:.2f}}<extra></extra>"))

    return traces


def __addFSCPTraces(refData: pd.Series, plotConf: tuple):
    traces = []

    ci_max, cost_max, n_samples = plotConf

    ci_samples = np.linspace(0.0, ci_max, n_samples)
    cost_samples = np.linspace(0.0, cost_max, n_samples)
    ci_v, cost_v = np.meshgrid(ci_samples, cost_samples)

    ci_ref = refData.ci
    cost_ref = refData.cost

    fscp = (cost_v - cost_ref)/(ci_ref - ci_v)

    # heatmap
    traces.append(go.Heatmap(x=ci_samples*1000, y=cost_samples, z=fscp,
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
                             )))

    # thin lines every 50
    traces.append(go.Contour(x=ci_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=False,
                                 start=50,
                                 end=3000,
                                 size=50,
                             )))

    # thick lines
    thickLines = [
        {'size': 100, 'start': 100, 'end': 600},
        {'size': 250, 'start': 750, 'end': 1000},
        {'size': 300, 'start': 1200, 'end': 1500},
    ]
    for kwargs in thickLines:
        traces.append(go.Contour(
            x=ci_samples*1000, y=cost_samples, z=fscp,
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
