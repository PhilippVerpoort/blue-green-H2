from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.timeit import timeit


@timeit
def plotOverTime(FSCPData: pd.DataFrame, config: dict):
    # select which lines to plot based on function argument
    plotScatter, plotLines = __selectPlotFSCPs(FSCPData, config['selected_cases'], config['n_samples'])

    # produce figure
    fig = __produceFigure(plotScatter, plotLines, config)

    # styling figure
    __styling(fig, config)

    return {'fig3': fig}


def __selectPlotFSCPs(FSCPData: pd.DataFrame, selected_cases: dict, n_samples: int):
    listOfFSCPs = []

    for fuels in selected_cases.values():
        selected_FSCPs = FSCPData.query(f"fuel_x in @fuels & fuel_y in @fuels & year_x==year_y")\
                                 .rename(columns={'year_x': 'year'})\
                                 .drop(columns=['year_y'])\
                                 .assign(tid=lambda r: r.fuel_x + ' to ' + r.fuel_y)\
                                 .reset_index(drop=True)
        listOfFSCPs.append(selected_FSCPs)

    plotFSCPs = pd.concat(listOfFSCPs)
    plotScatter = plotFSCPs[['tid', 'fuel_x', 'fuel_y', 'year', 'fscp', 'fscp_uu', 'fscp_ul']]
    plotLines = plotFSCPs[['tid', 'fuel_x', 'fuel_y', 'year', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']]

    # interpolation of plotLines
    t = np.linspace(plotLines['year'].min(), plotLines['year'].max(), n_samples)
    dtypes = {'year': float, 'cost_x': float, 'cost_y': float, 'ghgi_x': float, 'ghgi_y': float}
    allEntries = []

    for tid in plotLines.tid.unique():
        fuel_x, fuel_y = tid.split(' to ')

        samples = plotLines.query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}'")\
                           .reset_index(drop=True)\
                           .astype(dtypes)
        new = dict(
            tid=n_samples * [tid],
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

    return plotScatter, plotLinesInterpolated


def __produceFigure(plotScatter: pd.DataFrame, plotLines: pd.DataFrame, config: dict):
    # plot
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=ascii_lowercase,
        shared_yaxes=True,
        horizontal_spacing=0.025,
        vertical_spacing=0.1,
    )

    subfigs = [(k//2+1, k%2+1, scid) for k, scid in enumerate(config['selected_cases'])]


    # add FSCP traces
    all_traces = __addFSCPTraces(plotScatter, plotLines, config)
    hasLegend = []
    for i, j, scid in subfigs:
        for tid, traces in all_traces.items():
            tid_techs = '-'.join([fuel.split('-')[0] for fuel in tid.split(' to ')])
            if all(fuel in config['selected_cases'][scid] for fuel in tid.split(' to ')):
                for trace in traces:
                    if tid_techs in hasLegend:
                        trace.showlegend = False
                    fig.add_trace(trace, row=i, col=j)
                if tid_techs not in hasLegend:
                    hasLegend.append(tid_techs)


    # compute and plot carbon price tracjetory
    cpTrajData = __computeCPTraj(config['co2price_traj']['years'], config['co2price_traj']['values'], config['n_samples'])
    traces = __addCPTraces(cpTrajData, config)
    for trace in traces:
        for i, j, scid in subfigs:
            if i>1 or j>1: trace.showlegend = False
            fig.add_trace(trace, row=i, col=j)


    # zero y line
    for i, j, _ in subfigs:
        fig.add_hline(0.0, line_width=config['global']['lw_thin'], line_color='black', row=i, col=j)


    # add text annotations explaining figure content
    annotationStyling = dict(xanchor='right', yanchor='top', showarrow=False,
                             bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

    for k, scid in enumerate(config['selected_cases']):
        axisNumb = str(k+1) if k else ''
        fig.add_annotation(
            x=0.99,
            xref=f"x{axisNumb} domain",
            y=0.98,
            yref=f"y{axisNumb} domain",
            text=f"{config['selected_cases_labels'][scid]}: {config['selected_cases'][scid][-2]} vs. {config['selected_cases'][scid][-1]}",
            **annotationStyling
        )

    # add circles on intersects
    __addAnnotations(fig, cpTrajData, plotLines, config)


    # # add arrows in 2025
    # __addAnnotationArrows(fig, config)


    # add legend for annotations
    __addAnnotationsLegend(fig, config)


    # add top and left annotation
    annotationStyling = dict(xanchor='center', yanchor='middle', showarrow=False,
                             bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

    for i in range(2):
        fig.add_annotation(
            x=0.50,
            xref=f"x{str(i+1) if i else ''} domain",
            y=1.15,
            yref=f"y domain",
            text=config['sidelabels']['top'][i],
            **annotationStyling
        )

        fig.add_annotation(
            x=-0.17,
            xref=f"x domain",
            y=0.5,
            yref=f"y{str(i+2) if i else ''} domain",
            text=config['sidelabels']['left'][i],
            textangle=-90,
            **annotationStyling
        )


    # update axes titles and ranges
    fig.update_layout(
        **{f"xaxis{i+1 if i else ''}": dict(
            title=config['labels']['time'],
            range=[config['plotting']['t_min'], config['plotting']['t_max']]
        ) for i in range(4)},
        **{f"yaxis{i+1 if i else ''}": dict(
            title=config['labels']['fscp'] if (i+1)%2 else '',
            range=[config['plotting']['fscp_min'], config['plotting']['fscp_max']]
        ) for i in range(4)},
        margin_l=180.0,
        margin_b=520.0,
    )

    return fig


def __addFSCPTraces(plotScatter: pd.DataFrame, plotLines: pd.DataFrame, config: dict, sensitivityNG: bool = False):
    traces = {}

    for tid in plotScatter.tid.unique():
        thisTraces = []

        thisScatter = plotScatter.query(f"tid=='{tid}'").reset_index(drop=True)
        thisLine = plotLines.query(f"tid=='{tid}'").reset_index(drop=True)

        # line properties
        fuel_x = thisScatter.iloc[thisScatter.first_valid_index()]['fuel_x']
        fuel_y = thisScatter.iloc[thisScatter.first_valid_index()]['fuel_y']
        name = f"Fossil→{config['shortnames'][fuel_y]}" if fuel_x.startswith('NG') else f"{config['shortnames'][fuel_x]}→{config['shortnames'][fuel_y]}"
        col = config['fscp_colour'][fuel_x.split('-')[0]] if 'NG' not in tid else config['colours'][fuel_y]
        isbluegreen = 'NG' in fuel_x

        # scatter plot
        thisTraces.append(go.Scatter(
            x=thisScatter['year'],
            y=thisScatter['fscp'],
            name=name,
            legendgroup=0 if isbluegreen else 1,
            showlegend=False,
            mode='markers',
            line=dict(color=col, width=config['global']['lw_default']), #, dash='dot' if dashed else 'solid'),
            marker=dict(symbol='x-thin', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': col}, ),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))

        # line plot
        thisTraces.append(go.Scatter(
            x=thisLine['year'],
            y=thisLine['fscp'],
            legendgroup=0 if isbluegreen else 1,
            legendgrouptitle=dict(text=f"<b>{config['legendlabels'][0]}:</b>" if isbluegreen else f"<b>{config['legendlabels'][1]}:</b>"),
            name=name,
            mode='lines',
            line=dict(color=col, width=config['global']['lw_default']), #, dash='dot' if dashed else 'dash' if longdashed else 'solid'),
        ))

        traces[tid] = thisTraces

    return traces


def __addAnnotations(fig: go.Figure, cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, config: dict):
    #scid_include = ['green-supreme', 'competitive']

    for i, j, scid in [(k//2+1, k%2+1, scid) for k, scid in enumerate(config['selected_cases'])]:
        points = __calcPoints(cpTrajData, plotLines, config['selected_cases'][scid])
        data = pd.DataFrame(points).T.query(f"delta < 5.0")

        fig.add_trace(go.Scatter(
            x=data.year,
            y=data.fscp,
            text=data.index,
            mode='markers+text',
            marker=dict(symbol='circle-open', size=config['global']['highlight_marker'], line={'width': config['global']['lw_thin']}, color='Black'),
            textposition='bottom center',
            showlegend=False,
            # hovertemplate = f"{name}<br>Carbon price: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<extra></extra>",
        ), row=i, col=j)


def __calcPoints(cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, fuels: list) -> dict:
    points = {}

    fuelRef, fuelBlue, fuelGreen = fuels

    dropCols = ['tid', 'fuel_x', 'fuel_y', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']
    greenLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)
    blueLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelBlue}'").drop(columns=dropCols).reset_index(drop=True)
    redLine = plotLines.query(f"fuel_x=='{fuelBlue}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)

    purpleLine = cpTrajData.drop(columns=['name', 'CP_u', 'CP_l'])

    for i, line in enumerate([blueLine, greenLine, redLine]):
        diffLines = pd.merge(line, purpleLine, on=['year'])
        diffLines['delta'] = (diffLines['fscp'] - diffLines['CP']).abs()
        points[i+2] = diffLines.nsmallest(1, 'delta').drop(columns=['CP']).iloc[0]

    diffLines = pd.merge(blueLine, greenLine, on=['year'], suffixes=('', '_right'))
    diffLines['delta'] = (diffLines['fscp'] - diffLines['fscp_right']).abs()
    points[5] = diffLines.nsmallest(1, 'delta').drop(columns=['fscp_right']).iloc[0]

    points[6] = redLine.abs().nsmallest(1, 'fscp').assign(delta=lambda r: r.fscp).iloc[0]

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
