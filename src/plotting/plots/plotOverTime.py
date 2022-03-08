from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.timeit import timeit


@timeit
def plotOverTime(FSCPData: pd.DataFrame, FSCPDataSteel: pd.DataFrame, config: dict):
    # select which lines to plot based on function argument
    FSCPsCols, plotFSCP, plotLines = __selectPlotFSCPs(FSCPData, config['showFSCPs'], config['refFuelTop'],
                                                       config['n_samples'])
    FSCPsCols, plotFSCPSteel, plotLinesSteel = __selectPlotFSCPs(FSCPDataSteel, config['showFSCPs'],
                                                                 config['refFuelBottom'], config['n_samples'])

    # produce figure
    fig = __produceFigure(FSCPsCols, plotFSCP, plotFSCPSteel, plotLines, plotLinesSteel, config)

    # styling figure
    __styling(fig, config)

    return {'fig3': fig}


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
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=ascii_lowercase,
        shared_yaxes=True,
        horizontal_spacing=0.025,
        vertical_spacing=0.1,
    )


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
    cpTrajData = __computeCPTraj(config['co2price_traj']['years'], config['co2price_traj']['values'], config['n_samples'])
    traces = __addCPTraces(cpTrajData, config)
    for trace in traces:
        for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            if i or j: trace.showlegend = False
            fig.add_trace(trace, row=i + 1, col=j + 1)


    # zero y line
    for i, j in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        fig.add_hline(0.0, line_width=config['global']['lw_thin'], line_color='black', row=i + 1, col=j + 1)


    # add text annotations explaining figure content
    annotationStyling = dict(xanchor='center', yanchor='middle', showarrow=False,
                             bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

    for i in range(2):
        axisNumb = str(i+1) if i else ''
        blueTech = config['annotationLabels']['blueTechs'][i]
        fig.add_annotation(
            x=0.50,
            xref=f"x{axisNumb} domain",
            y=1.15,
            yref=f"y{axisNumb} domain",
            text=f"Blue H<sub>2</sub> from {blueTech}",
            **annotationStyling
        )

    for i in range(2):
        axisNumb = str(i+2) if i else ''
        application = config['annotationLabels']['applications'][i]
        fig.add_annotation(
            x=-0.17,
            xref=f"x{axisNumb} domain",
            y=0.5,
            yref=f"y{axisNumb} domain",
            text=f"{application}",
            textangle=-90,
            **annotationStyling
        )


    # add circles on intersects
    __addAnnotations(fig, cpTrajData, plotLines, plotLinesSteel, config)


    # add arrows in 2025
    __addAnnotationArrows(fig, config)


    # add legend for annotations
    __addAnnotationsLegend(fig, config)


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
        margin_l=180.0,
        margin_b=520.0,
    )

    return fig


def __addAnnotations(fig: go.Figure, cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, plotLinesSteel: pd.DataFrame, config: dict):
    traceArgs = [
        dict(row=1, col=1, lines=plotLines, anno=config['annotationFuels']['left']),
        dict(row=1, col=2, lines=plotLines, anno=config['annotationFuels']['right']),
        dict(row=2, col=1, lines=plotLinesSteel, anno=config['annotationFuels']['left']),
        dict(row=2, col=2, lines=plotLinesSteel, anno=config['annotationFuels']['right']),
    ]

    for args in traceArgs:
        points = __calcPoints(cpTrajData, args['lines'], args['anno'])
        data = pd.DataFrame(points).T

        fig.add_trace(go.Scatter(
            x=data.year,
            y=data.fscp,
            text=data.index,
            mode='markers+text',
            marker=dict(symbol='circle-open', size=config['global']['highlight_marker'], line={'width': config['global']['lw_thin']}, color='Black'),
            textposition='bottom center',
            showlegend=False,
            # hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<extra></extra>",
        ), row=args['row'], col=args['col'])


def __calcPoints(cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, fuels: list) -> dict:
    points = {}

    fuelRef, fuelGreen, fuelBlue = fuels

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


def __addAnnotationArrows(fig: go.Figure, config: dict):
    __addArrow(fig, 2025.0, 150.0, 600.0, 1, 1, config)
    __addArrow(fig, 2025.5, 150.0, 800.0, 1, 1, config)
    fig.add_annotation(text='1', x=2024.5, y=200.0, row=1, col=1, showarrow=False)

    __addArrow(fig, 2025.0, 150.0, 300.0, 1, 2, config)
    __addArrow(fig, 2025.5, 150.0, 800.0, 1, 2, config)
    fig.add_annotation(text='1', x=2024.5, y=200.0, row=1, col=2, showarrow=False)

    __addArrow(fig, 2024.5, 90.0, 200.0, 2, 1, config)
    fig.add_annotation(text='1', x=2024.0, y=150.0, row=2, col=1, showarrow=False)

    __addArrow(fig, 2024.5, 90.0, 200.0, 2, 2, config)
    fig.add_annotation(text='1', x=2024.0, y=150.0, row=2, col=2, showarrow=False)


def __addArrow(fig: go.Figure, x: float, y1: float, y2: float, row: int, col: int, config: dict):
    xaxes = [['x', 'x2'], ['x3', 'x4']]
    yaxes = [['y', 'y2'], ['y3', 'y4']]
    
    for ay, y in [(y1, y2), (y2, y1)]:
        fig.add_annotation(
            axref=xaxes[row-1][col-1],
            xref=xaxes[row-1][col-1],
            ayref=yaxes[row-1][col-1],
            yref=yaxes[row-1][col-1],
            ax=x,
            x=x,
            ay=ay,
            y=y,
            arrowcolor='black',
            arrowwidth=config['global']['lw_thin'],
            #arrowsize=config['global']['highlight_marker_sm'],
            arrowhead=2,
            showarrow=True,
            row=row,
            col=col,
        )


def __addAnnotationsLegend(fig: go.Figure, config: dict):
    y0 = -0.40

    fig.add_shape(
        type='rect',
        x0=0.0,
        y0=y0,
        x1=0.80,
        y1=y0-0.2,
        xref='paper',
        yref='paper',
        line_width=2,
        fillcolor='white',
    )

    fig.add_annotation(
        text=f"<b>{config['annotationTexts']['heading1']}:</b><br><br><br><b>{config['annotationTexts']['heading2']}:</b>",
        align='left',
        xanchor='left',
        x=0.0,
        yanchor='top',
        y=y0,
        xref='paper',
        yref='paper',
        showarrow=False,
    )

    for i in range(6):
        fig.add_annotation(
            text=f"{i+1}: "+config['annotationTexts'][f"point{i+1}"],
            align='left',
            xanchor='left',
            x=0.0 + i%3 * 0.22,
            yanchor='top',
            y=y0-(0.03 if i<3 else 0.13),
            xref='paper',
            yref='paper',
            showarrow=False,
        )



def __addFSCPTraces(plotData: pd.DataFrame, plotLines: pd.DataFrame, n_lines: int, refFuel: str, config: dict, sensitivityNG: bool = False):
    traces = []

    for index in range(n_lines):
        thisDataScatter = plotData.query(f"plotIndex=={index}").reset_index(drop=True)
        thisDataLine = plotLines.query(f"plotIndex=={index}").reset_index(drop=True)

        # styling of individual lines
        truncated = (thisDataScatter.loc[0, 'fuel_x'] == 'blue LEB' and thisDataScatter.loc[0, 'fuel_y'] == 'green RE') or \
                    thisDataScatter.loc[0, 'fuel_x'] == 'blue LEB lowscco2'
        dashed = thisDataScatter.loc[0, 'fuel_y'] in ['green pure RE', 'blue LEB lowscco2']
        longdashed = thisDataScatter.loc[0, 'fuel_x'] == 'blue LEB lowscco2'
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
        name = f"Fossil→{config['names'][fuel_y]}" if fuel_x == 'ref' else f"{config['names'][fuel_x]}→{config['names'][fuel_y]}"
        col = config['fscp_colours'][f"{fuel_x} to {fuel_y}"] if f"{fuel_x} to {fuel_y}" in config['fscp_colours'] else \
        config['colours'][fuel_y]

        # do not plot awkward red line in sensitivity analysis row 2
        if sensitivityNG and fuel_x == 'blue LEB':
            continue

        # scatter plot
        traces.append((index, go.Scatter(
            x=thisDataScatter['year'],
            y=thisDataScatter['fscp'],
            name=name,
            legendgroup=0 if fuel_x == 'ref' else 1,
            showlegend=False,
            mode='markers',
            line=dict(color=col, width=config['global']['lw_default'], dash='dot' if dashed else 'solid'),
            marker=dict(symbol='x-thin', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': col}, ),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        )))

        # remove unphysical negative FSCPs
        if truncated and not sensitivityNG:
            thisDataLine = thisDataLine.query(f"(year>=2030 & fscp>0.0) | year>=2040")

        # line plot
        traces.append((index, go.Scatter(
            x=thisDataLine['year'],
            y=thisDataLine['fscp'],
            legendgroup=0 if fuel_x == 'ref' else 1,
            legendgrouptitle=dict(text=f"<b>{config['legendlabels'][0]}:</b>" if fuel_x=='ref' else f"<b>{config['legendlabels'][0]}:</b>"),
            name=name,
            mode='lines',
            line=dict(color=col, width=config['global']['lw_default'], dash='dot' if dashed else 'dash' if longdashed else 'solid'),
        )))

        # error bars
        thisDataScatter = thisDataScatter.query(f"year==[2030,2040,2050]")
        thisDataScatter = thisDataScatter.query(f"fscp<={config['plotting']['fscp_max']} and (fscp>0.0 | year > 2040)")

        traces.append((index, go.Scatter(
            x=thisDataScatter['year'] + shift * 0.1,
            y=thisDataScatter['fscp'],
            error_y=dict(type='data', array=thisDataScatter['fscp_uu'], arrayminus=thisDataScatter['fscp_ul'],
                         thickness=config['global']['lw_thin']),
            name=name,
            legendgroup=0 if fuel_x == 'ref' else 1,
            showlegend=False,
            mode='markers',
            marker=dict(symbol='x-thin', size=0.00001,),
            line_color=('rgba({}, {}, {}, {})'.format(*hex_to_rgb(col), .4)),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        )))

    return traces


# compute carbon price trajectories
def __computeCPTraj(years: list, values: dict, n_samples: int):
    v_mean = []
    v_upper = []
    v_lower = []

    for i, year in enumerate(years):
        vals = [v[i] for v in values.values()]
        mean = sum(vals)/len(vals)
        v_mean.append(mean)
        v_upper.append(max(vals)-mean)
        v_lower.append(mean-min(vals))

    # create data frame with time and cp values
    cpData = pd.DataFrame({
        'year': years,
        'CP': v_mean,
        'CP_u': v_upper,
        'CP_l': v_lower,
    })

    # interpolate in between
    samples = pd.DataFrame({'year': np.linspace(years[0], years[-1], n_samples)})
    dtypes = {'year': float, 'CP': float, 'CP_u': float, 'CP_l': float}
    cpData = cpData.merge(samples, how='outer').sort_values(by=['year']).astype(dtypes).interpolate()

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
        legendgroup=1,
        mode='lines',
        x=cpTrajData['year'],
        y=cpTrajData['CP'],
        line_color=colour,
        line_width=config['global']['lw_thin'],
        showlegend=True,
        hovertemplate=f"<b>{name}</b><br>Time: %{{x:.2f}}<br>Carbon price: %{{y:.2f}}<extra></extra>"
    ))

    data_x = cpTrajData['year']
    data_yu = cpTrajData['CP'] + cpTrajData['CP_u']
    data_yl = cpTrajData['CP'] - cpTrajData['CP_l']

    errorBand = go.Scatter(
        name='Uncertainty Range',
        legendgroup=1,
        x=pd.concat([data_x, data_x[::-1]], ignore_index=True),
        y=pd.concat([data_yl, data_yu[::-1]], ignore_index=True),
        mode='lines',
        marker=dict(color=colour),
        fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(colour))),
        fill='toself',
        line=dict(width=config['global']['lw_ultrathin']),
        showlegend=False,
        hoverinfo='skip'
    )
    traces.append(errorBand)

    return traces


def __styling(fig: go.Figure, config: dict):
    # update legend styling
    fig.update_layout(
        legend=dict(
            orientation='h',
            xanchor='left',
            x=0.0,
            yanchor='top',
            y=-0.1,
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
