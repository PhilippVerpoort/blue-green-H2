from string import ascii_lowercase

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig1(fuelData: pd.DataFrame, fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotData, linesCols = __selectPlotData(fuelData, config['showFuels'])

    # select which FSCPs to plot based on function argument
    plotFSCP, FSCPsCols = __selectPlotFSCPs(FSCPData, config['showFSCPs'])

    # produce figure
    fig = __produceFigure(plotData, linesCols, plotFSCP, FSCPsCols, config)

    # write figure to image file
    if export_img:
        w_mm = 180.0
        h_mm = 61.0

        fs_sm = getFontSize(5.0)
        fs_lg = getFontSize(7.0)

        fig.update_layout(font_size=fs_sm)
        fig.update_annotations(font_size=fs_lg)
        fig.update_xaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)
        fig.update_yaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)

        fig.write_image("output/fig1.png", **getImageSize(w_mm, h_mm))

    return fig


def __selectPlotData(fuelData: pd.DataFrame, showFuels: dict = None):
    linesCols = {}

    if showFuels is None:
        plotData = fuelData.query("year == 2020")
    else:
        plotData = pd.DataFrame(columns=fuelData.keys())
        for cols, year, fuel in showFuels:
            addFuel = fuelData.query("year=={} & fuel=='{}'".format(year, fuel)).reset_index(drop=True)
            addFuel.index += len(plotData)
            linesCols[len(plotData)] = cols
            plotData = pd.concat([plotData, addFuel])

    return plotData, linesCols


def __selectPlotFSCPs(FSCPData: pd.DataFrame, showFSCPs: dict = None):
    FSCPsCols = {}

    if showFSCPs is None:
        plotFSCP = FSCPData.query("year_x==2020 & year_y==2020")
    else:
        plotFSCP = pd.DataFrame(columns=(list(FSCPData.keys()) + ['symbol']))
        for cols, year_x, fuel_x, year_y, fuel_y, symbol in showFSCPs:
            addFSCP = FSCPData.query("year_x=={} & fuel_x=='{}' & year_y=={} & fuel_y=='{}'".format(year_x, fuel_x, year_y, fuel_y))
            addFSCP.insert(len(addFSCP.columns), 'symbol', symbol)
            addFSCP.index += len(plotFSCP)
            FSCPsCols[len(plotFSCP)] = cols
            plotFSCP = pd.concat([plotFSCP, addFSCP], ignore_index = True)

    return plotFSCP, FSCPsCols


def __produceFigure(plotData: pd.DataFrame, linesCols: dict, plotFSCP: pd.DataFrame, FSCPsCols: dict, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=config['plotting']['numb_cols'],
                        subplot_titles=ascii_lowercase,
                        shared_yaxes=True,
                        horizontal_spacing=0.025,)


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


    # update axes titles and ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['CP'],
            range=[0.0, config['plotting']['carb_price_max']],
        ),
        xaxis2=dict(
            title=config['labels']['CP'],
            range=[0.0, config['plotting']['carb_price_max']],
        ),
        yaxis=dict(
            title=config['labels']['total_cost'],
            range=[0.0, config['plotting']['fuel_cost_max']],
        )
    )


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
    for axis in ['xaxis', 'xaxis2', 'yaxis', 'yaxis2']:
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
        y_uu = np.sqrt(row.cost_uu**2 + row.ci_uu**2 * x**2)
        y_ul = np.sqrt(row.cost_ul**2 + row.ci_ul**2 * x**2)

        # fuel line
        traces.append((index, go.Scatter(x=x, y=y,
            name=f"{name} ({year})",
            legendgroup=f"{fuel}_{year}",
            mode="lines",
            line=dict(color=col, width=5, dash='dash' if occurrence[fuel]>1 else 'solid'),
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
                line=dict(width=.6),
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
                                 marker=dict(symbol=row.symbol, size=24, line={'width': 4}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

        # dashed line to x-axis
        traces.append((index, go.Scatter(x=(row.fscp, row.fscp), y = (0, row.fscp_tc),
                                 mode="lines",
                                 line=dict(color='Black', width=3, dash='dot'),
                                 showlegend=False, hoverinfo='none',)))

        # error bar near x-axis
        traces.append((index, go.Scatter(x=(row.fscp,), y = (0,),
                                 error_x=dict(type='data', array=(row.fscp_uu,), arrayminus=(row.fscp_ul,)) if config['plotting']['uncertainty'] else None,
                                 marker=dict(symbol='x-thin', size=10, line={'width': 4}, color='Black'),
                                 showlegend=False,
                                 hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>")))

    return traces
