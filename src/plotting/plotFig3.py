from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig3(FSCPData: pd.DataFrame, FSCPDataSteel: pd.DataFrame, config: dict, export_img: bool = True):
    # select which lines to plot based on function argument
    FSCPsCols, plotFSCP, plotLines = __selectPlotFSCPs(FSCPData, config['showFSCPs'], config['refFuelTop'],
                                                       config['n_samples'])
    FSCPsCols, plotFSCPSteel, plotLinesSteel = __selectPlotFSCPs(FSCPDataSteel, config['showFSCPs'],
                                                                 config['refFuelBottom'], config['n_samples'])

    # produce figure
    fig = __produceFigure(FSCPsCols, plotFSCP, plotFSCPSteel, plotLines, plotLinesSteel, config)

    # styling figure
    __styling(fig, config)

    # write figure to image file
    if export_img:
        w_mm = 180.0
        h_mm = 122.0

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

        fig.write_image("output/fig3.png", **getImageSize(w_mm, h_mm))

    return fig


def __selectPlotFSCPs(FSCPData: pd.DataFrame, showFSCPs: dict, refFuel: str, n_samples: int):
    FSCPsCols = [None] * len(showFSCPs)

    listOfFSCPs = pd.DataFrame(columns=(FSCPData.keys().tolist() + ['plotIndex']))
    for index, args in enumerate(showFSCPs):
        cols, fuel_x, fuel_y = args
        if fuel_x == 'ref': fuel_x = refFuel
        addFSCP = FSCPData.query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y").reset_index(drop=True)
        if fuel_x == refFuel: addFSCP.loc[:, 'fuel_x'] = 'ref'
        addFSCP.insert(1, 'plotIndex', len(addFSCP) * [index])
        FSCPsCols[index] = cols
        listOfFSCPs = pd.concat([listOfFSCPs, addFSCP], ignore_index=True)

    # year_x == year_y, so we only need one of them from now on
    listOfFSCPs['year'] = listOfFSCPs['year_x']

    # return FSCPs for scatter plots
    plotFSCP = listOfFSCPs[['plotIndex', 'fuel_x', 'fuel_y', 'year', 'fscp', 'fscp_uu', 'fscp_ul']]

    # return costs and GHGIs for line plots
    plotLines = listOfFSCPs[['plotIndex', 'fuel_x', 'fuel_y', 'year', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']]

    # interpolation of plotLines
    t = np.linspace(plotLines['year'].min(), plotLines['year'].max(), n_samples)
    dtypes = {'year': float, 'cost_x': float, 'cost_y': float, 'ghgi_x': float, 'ghgi_y': float}
    allEntries = []

    for index in plotLines['plotIndex'].unique():
        samples = plotLines.query(f"plotIndex=={index}").reset_index(drop=True).astype(dtypes)
        fuel_x = samples.fuel_x.iloc[0]
        fuel_y = samples.fuel_y.iloc[0]
        new = dict(
            plotIndex=n_samples * [int(index)],
            fuel_x=n_samples * [fuel_x],
            fuel_y=n_samples * [fuel_y],
            year=t,
        )
        tmp = pd.DataFrame(new, columns=plotLines.keys())
        tmp.index = np.arange(len(samples), len(tmp) + len(samples))
        tmp = tmp.merge(samples, how='outer').sort_values(by=['year']).astype(dtypes)
        allEntries.append(tmp.interpolate())

    plotLinesInterpolated = pd.concat(allEntries, ignore_index=True)
    plotLinesInterpolated['fscp'] = (plotLinesInterpolated['cost_x'] - plotLinesInterpolated['cost_y']) / (
                plotLinesInterpolated['ghgi_y'] - plotLinesInterpolated['ghgi_x'])

    return FSCPsCols, plotFSCP, plotLinesInterpolated


def __produceFigure(FSCPsCols: list, plotFSCP: pd.DataFrame, plotFSCPSteel: pd.DataFrame,
                    plotLines: pd.DataFrame, plotLinesSteel: pd.DataFrame, config: dict):
    # plot
    fig = make_subplots(rows=2,
                        cols=2,
                        subplot_titles=ascii_lowercase,
                        shared_yaxes=True,
                        horizontal_spacing=0.025,
                        vertical_spacing=0.1, )

    # add FSCP traces for heating
    traces = __addFSCPTraces(plotFSCP, plotLines, len(FSCPsCols), config['refFuelTop'], config)
    for id, trace in traces:
        for j, col in enumerate(FSCPsCols[id]):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=col)

    # add FSCP traces for steel
    traces = __addFSCPTraces(plotFSCPSteel, plotLinesSteel, len(FSCPsCols), config['refFuelBottom'], config)
    for id, trace in traces:
        for j, col in enumerate(FSCPsCols[id]):
            trace.showlegend = False
            fig.add_trace(trace, row=2, col=col)

    # compute and plot carbon price tracjetory
    cpTrajData = __computeCPTraj(config['carbon_price_trajectory'], config['n_samples'])
    traces = __addCPTraces(cpTrajData, config)
    for trace in traces:
        for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            if i or j: trace.showlegend = False
            fig.add_trace(trace, row=i + 1, col=j + 1)

    # zero y line
    for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        fig.add_hline(0.0, line_width=3, line_color='black', row=i + 1, col=j + 1)

    # annotations
    __addAnnotations(fig, cpTrajData, plotLines, plotLinesSteel, config)


    # add annotations
    annotationStylingA = dict(xanchor='center', yanchor='top', showarrow=False, bordercolor='black', borderwidth=2,
                              borderpad=3, bgcolor='white')
    fig.add_annotation(x=0.5, xref="paper",
                       y=0.98 * config['plotting']['fscp_max'], yref="y",
                       text='Reference: Natural Gas in Heating', **annotationStylingA)
    fig.add_annotation(x=0.5, xref="paper",
                       y=0.98 * config['plotting']['fscp_max'], yref="y3",
                       text='Reference: Blast Furnace in Steel', **annotationStylingA)

    # update axes titles and ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['time'],
            range=[config['plotting']['t_min'], config['plotting']['t_max']]
        ),
        xaxis2=dict(
            title=config['labels']['time'],
            range=[config['plotting']['t_min'], config['plotting']['t_max']]
        ),
        xaxis3=dict(
            title=config['labels']['time'],
            range=[config['plotting']['t_min'], config['plotting']['t_max']]
        ),
        xaxis4=dict(
            title=config['labels']['time'],
            range=[config['plotting']['t_min'], config['plotting']['t_max']]
        ),
        yaxis=dict(
            title=config['labels']['fscp'],
            range=[config['plotting']['fscp_min'], config['plotting']['fscp_max']]
        ),
        yaxis3=dict(
            title=config['labels']['fscp_steel'],
            range=[config['plotting']['fscp_min'], config['plotting']['fscp_max']]
        ),
    )

    return fig


def __addAnnotations(fig: go.Figure, cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, plotLinesSteel: pd.DataFrame, config: dict):
    traceArgs = [
        dict(row=1, col=1, lines=plotLines, anno=config['showAnnotations']['left']),
        dict(row=1, col=2, lines=plotLines, anno=config['showAnnotations']['right']),
        dict(row=2, col=1, lines=plotLinesSteel, anno=config['showAnnotations']['left']),
        dict(row=2, col=2, lines=plotLinesSteel, anno=config['showAnnotations']['right']),
    ]

    for args in traceArgs:
        points = __calcPoints(cpTrajData, args['lines'], args['anno'])
        data = pd.DataFrame(points).T

        fig.add_trace(go.Scatter(
            x=data.year,
            y=data.fscp,
            text=data.index,
            mode='markers+text',
            marker=dict(symbol='circle-open', size=24, line={'width': 4}, color='Black'),
            textposition="bottom center",
            showlegend=False,
            # hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}±%{{error_x.array:.2f}}<extra></extra>",
        ), row=args['row'], col=args['col'])



def __calcPoints(cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, showAnnotations: list) -> dict:
    points = {}

    fuelRef, fuelGreen, fuelBlue = showAnnotations

    dropCols = ['plotIndex', 'fuel_x', 'fuel_y', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']
    greenLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)
    blueLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelBlue}'").drop(columns=dropCols).reset_index(drop=True)
    redLine = plotLines.query(f"fuel_x=='{fuelBlue}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)

    purpleLine = cpTrajData.drop(columns=['name', 'CP_u', 'CP_l'])

    for i, line in enumerate([blueLine, greenLine, redLine]):
        diffLines = pd.merge(line, purpleLine, on=['year'])
        diffLines['delta'] = (diffLines['fscp'] - diffLines['CP']).abs()
        points[i+2] = diffLines.nsmallest(1, 'delta').drop(columns=['CP', 'delta']).iloc[0]

    diffLines = pd.merge(blueLine, greenLine, on=['year'], suffixes=('', '_right'))
    diffLines['delta'] = (diffLines['fscp'] - diffLines['fscp_right']).abs()
    points[5] = diffLines.nsmallest(1, 'delta').drop(columns=['fscp_right', 'delta']).iloc[0]

    points[6] = redLine.abs().nsmallest(1, 'fscp').iloc[0]

    return points


def __addFSCPTraces(plotData: pd.DataFrame, plotLines: pd.DataFrame, n_lines: int, refFuel: str, config: dict):
    traces = []

    for index in range(n_lines):
        thisDataScatter = plotData.query(f"plotIndex=={index}").reset_index(drop=True)
        thisDataLine = plotLines.query(f"plotIndex=={index}").reset_index(drop=True)

        # styling of individual lines
        blueGreenSwitching = thisDataScatter.loc[0, 'fuel_x'] == 'blue LEB' and thisDataScatter.loc[
            0, 'fuel_y'] == 'green RE'
        dashed = thisDataScatter.loc[0, 'fuel_y'] == 'green pure RE'
        shift = 0
        if thisDataScatter.loc[0, 'fuel_y'] == 'green RE':
            if thisDataScatter.loc[0, 'fuel_x'] == 'ref':
                shift = -1
            else:
                shift = +1
        elif thisDataScatter.loc[0, 'fuel_y'] == 'green pure RE':
            shift = +2
            thisDataScatter = thisDataScatter.query(f"year<=2035")
            thisDataLine = thisDataLine.query(f"year<=2035")

        # line properties
        fuel_x = thisDataScatter.iloc[thisDataScatter.first_valid_index()]['fuel_x']
        fuel_y = thisDataScatter.iloc[0]['fuel_y']
        name = f"Reference to {config['names'][fuel_y]}" if fuel_x == 'ref' else f"{config['names'][fuel_x]} to {config['names'][fuel_y]}"
        col = config['fscp_colours'][f"{fuel_x} to {fuel_y}"] if f"{fuel_x} to {fuel_y}" in config['fscp_colours'] else \
        config['colours'][fuel_y]

        # scatter plot
        traces.append((index, go.Scatter(
            x=thisDataScatter['year'],
            y=thisDataScatter['fscp'],
            name=name,
            legendgroup=f"{fuel_x} {fuel_y}",
            showlegend=False,
            mode="markers",
            line=dict(color=col, width=4, dash='dash' if dashed else 'solid'),
            marker=dict(symbol='x-thin', size=10, line={'width': 3, 'color': col}, ),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>",
        )))

        # remove unphysical negative FSCPs
        if blueGreenSwitching:
            thisDataLine = thisDataLine.query(f"year>=2030")

        # line plot
        traces.append((index, go.Scatter(
            x=thisDataLine['year'],
            y=thisDataLine['fscp'],
            legendgroup=f"{fuel_x} {fuel_y}",
            showlegend=not dashed,
            name=name,
            mode="lines",
            line=dict(color=col, width=4, dash='dash' if dashed else 'solid'),
        )))

        # error bars
        thisDataScatter = thisDataScatter.query(f"year==[2030,2040,2050]")
        thisDataScatter = thisDataScatter.query(f"fscp<={config['plotting']['fscp_max']}")

        traces.append((index, go.Scatter(
            x=thisDataScatter['year'] + shift * 0.1,
            y=thisDataScatter['fscp'],
            error_y=dict(type='data', array=thisDataScatter['fscp_uu'], arrayminus=thisDataScatter['fscp_ul'],
                         thickness=3),
            name=name,
            legendgroup=f"{fuel_x} {fuel_y}",
            showlegend=False,
            mode="markers",
            marker=dict(symbol='x-thin', size=0.00001, ),
            line=dict(color=("rgba({}, {}, {}, {})".format(*hex_to_rgb(col), .4)), width=3),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>",
        )))

    return traces


# compute carbon price trajectories
def __computeCPTraj(params: dict, n_samples: int):
    # poly fit function
    t_fit = np.array(params['time'])
    p_fit = np.array(params['value'])
    p_fit_u = np.array(params['value_upper'])
    p_fit_l = np.array(params['value_lower'])
    poly = np.poly1d(np.polyfit(t_fit, p_fit, 2))
    poly_u = np.poly1d(np.polyfit(t_fit, p_fit_u, 2))
    poly_l = np.poly1d(np.polyfit(t_fit, p_fit_l, 2))

    # create data frame with time and cp values
    t = np.linspace(params['time'][0] - 5.0, params['time'][-1] + 5.0, n_samples)
    cpData = pd.DataFrame({
        'year': t,
        'CP': poly(t),
        'CP_u': poly_u(t) - poly(t),
        'CP_l': -(poly_l(t) - poly(t)),
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
        name=name,
        mode='lines',
        x=cpTrajData['year'],
        y=cpTrajData['CP'],
        line_color=colour,
        line_width=3,
        showlegend=True,
        hovertemplate=f"<b>{name}</b><br>Time: %{{x:.2f}}<br>Carbon price: %{{y:.2f}}<extra></extra>"
    ))

    data_x = cpTrajData['year']
    data_yu = cpTrajData['CP'] + cpTrajData['CP_u']
    data_yl = cpTrajData['CP'] - cpTrajData['CP_l']

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


def __styling(fig: go.Figure, config: dict):
    # update legend styling
    fig.update_layout(
        legend=dict(
            xanchor="right",
            x=0.9975,
            yanchor="top",
            y=0.445,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )

    # update axis styling
    for axis in ['xaxis', 'xaxis2', 'xaxis3', 'xaxis4', 'yaxis', 'yaxis2', 'yaxis3', 'yaxis4']:
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
