from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig3(fuelSpecs: dict, FSCPData: pd.DataFrame,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # select which lines to plot based on function argument
    plotFSCP, FSCPsCols = __selectPlotFSCPs(FSCPData, config['showFSCPs'])

    # produce figure
    fig = __produceFigure(plotFSCP, FSCPsCols, config)

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

        fig.write_image("output/fig3.png", **getImageSize(w_mm, h_mm))

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
                        subplot_titles=ascii_lowercase,
                        shared_yaxes=True,
                        horizontal_spacing=0.025)


    # add FSCP traces
    traces = __addFSCPTraces(plotFSCP, len(FSCPsCols), config)
    for id, trace in traces:
        for j, col in enumerate(FSCPsCols[id]):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=col)


    # compute and plot carbon price tracjetory
    cpTrajData = __computeCPTraj(config['carbon_price_trajectory'])
    traces = __addCPTraces(cpTrajData, config)
    for trace in traces:
        for j in range(config['plotting']['numb_cols']):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=j+1)


    # update axes titles and ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['time'],
            range=[2024, 2051]
        ),
        xaxis2=dict(
            title=config['labels']['time'],
            range=[2024, 2051]
        ),
        yaxis=dict(
            title=config['labels']['fscp'],
            range=[0.0, config['plotting']['fscp_max']]
        )
    )


    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=1.2,
            xanchor="center",
            x=0.25,
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
            error_y=dict(type='data', array=thisData['fscp_u'], thickness=3),
            name=name,
            legendgroup=f"{fuel_x} {fuel_y}",
            mode="lines+markers",
            line=dict(color=col, width=5),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>")))

    return traces


# compute carbon price trajectories
def __computeCPTraj(params: dict):
    # poly fit function
    t_fit = np.array(params['time'])
    p_fit = np.array(params['value'])
    p_fit_u = np.array(params['value_upper'])
    p_fit_l = np.array(params['value_lower'])
    poly   = np.poly1d(np.polyfit(t_fit, p_fit, 2))
    poly_u = np.poly1d(np.polyfit(t_fit, p_fit_u, 2))
    poly_l = np.poly1d(np.polyfit(t_fit, p_fit_l, 2))


    # create data frame with time and cp values
    t = np.linspace(params['time'][0]-5.0, params['time'][-1]+5.0, 300)
    cpData = pd.DataFrame({
        'year': t,
        'CP': poly(t),
        'CP_u':   poly_u(t)-poly(t),
        'CP_l': -(poly_l(t)-poly(t)),
    })


    # add name to dataframe
    cpData['name'] = 'cp'

    return cpData


# plot traces
def __addCPTraces(cpTrajData: pd.DataFrame, config: dict):
    traces = []

    name = config['carbon_price_config']['name']
    colour = config['carbon_price_config']['colour']

    # add main graphs (FSCP and CP)
    traces.append(go.Scatter(
        name = name,
        mode = 'lines',
        x = cpTrajData['year'],
        y = cpTrajData['CP'],
        line_color = colour,
        line_width = 3,
        showlegend = True,
        hovertemplate=f"<b>{name}</b><br>Time: %{{x:.2f}}<br>Carbon price: %{{y:.2f}}<extra></extra>"
    ))

    data_x = cpTrajData['year']
    data_yu = cpTrajData['CP']+cpTrajData['CP_u']
    data_yl = cpTrajData['CP']-cpTrajData['CP_l']

    errorBand = go.Scatter(
        name='Uncertainty Range',
        x=pd.concat([data_x, data_x[::-1]], ignore_index=True),
        y=pd.concat([data_yl, data_yu[::-1]], ignore_index=True),
        mode='lines',
        marker=dict(color=colour),
        fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(colour))),
        fill='toself',
        line=dict(width=.6),
        showlegend=False,
        hoverinfo='skip'
    )
    traces.append(errorBand)

    return traces
