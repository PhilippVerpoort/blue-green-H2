import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.data.FSCPs.calc_FSCPs import calcFSCPFromCostAndGHGI
from src.timeit import timeit


@timeit
def plotOverTime(FSCPData: pd.DataFrame, config: dict, subfigs_needed: list, is_webapp: bool = False):
    ret = {}

    # select which lines to plot based on function argument
    plotScatter, plotLines = __selectPlotFSCPs(FSCPData, config['selected_cases'], config['n_samples'])

    # produce figure 3
    ret['fig3'] = __produceFigure(plotScatter, plotLines, config, is_webapp) if 'fig3' in subfigs_needed else None

    # produce figure S2
    ret['figS2'] = __produceFigure(plotScatter, plotLines, config, is_webapp, is_uncertainty=True) if 'figS2' in subfigs_needed else None

    return ret


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
    plotScatter = plotFSCPs[['tid', 'fuel_x', 'type_x', 'fuel_y', 'type_y', 'year', 'fscp', 'fscp_uu', 'fscp_ul']]
    plotLines = plotFSCPs[[
        'tid', 'fuel_x', 'type_x', 'fuel_y', 'type_y', 'year',
        'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y',
        'cost_uu_x', 'cost_uu_y', 'ghgi_uu_x', 'ghgi_uu_y',
        'cost_ul_x', 'cost_ul_y', 'ghgi_ul_x', 'ghgi_ul_y'
    ]]

    # interpolation of plotLines
    t = np.linspace(plotLines['year'].min(), plotLines['year'].max(), n_samples)
    dtypes = {
        'year': float,
        'cost_x': float, 'cost_y': float, 'ghgi_x': float, 'ghgi_y': float,
        'cost_uu_x': float, 'cost_uu_y': float, 'ghgi_uu_x': float, 'ghgi_uu_y': float,
        'cost_ul_x': float, 'cost_ul_y': float, 'ghgi_ul_x': float, 'ghgi_ul_y': float
    }
    allEntries = []

    for tid in plotLines.tid.unique():
        fuel_x, fuel_y = tid.split(' to ')
        type_x = plotLines.query(f"fuel_x=='{fuel_x}'").type_x.tolist()[0]
        type_y = plotLines.query(f"fuel_y=='{fuel_y}'").type_y.tolist()[0]

        samples = plotLines.query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}'")\
                           .reset_index(drop=True)\
                           .astype(dtypes)
        new = dict(
            tid=n_samples * [tid],
            fuel_x=n_samples * [fuel_x],
            type_x=n_samples * [type_x],
            fuel_y=n_samples * [fuel_y],
            type_y=n_samples * [type_y],
            year=t,
        )
        tmp = pd.DataFrame(new, columns=plotLines.keys()).astype(dtypes)
        tmp.index = np.arange(len(samples), len(tmp) + len(samples))
        tmp = tmp.merge(samples, how='outer').sort_values(by=['year'])
        allEntries.append(tmp.interpolate())

    plotLinesInterpolated = pd.concat(allEntries, ignore_index=True)

    plotLinesInterpolated['correlated'] = 0.0
    plotLinesInterpolated.loc[(plotLinesInterpolated['type_x'] != 'GREEN') & (plotLinesInterpolated['type_y'] != 'GREEN'), 'correlated'] = 1.0

    fscp, fscpu = calcFSCPFromCostAndGHGI(
        plotLinesInterpolated['cost_x'],
        plotLinesInterpolated['ghgi_x'],
        plotLinesInterpolated['cost_y'],
        plotLinesInterpolated['ghgi_y'],
        [plotLinesInterpolated[f"cost_{i}_x"] for i in ['uu', 'ul']],
        [plotLinesInterpolated[f"ghgi_{i}_x"] for i in ['uu', 'ul']],
        [plotLinesInterpolated[f"cost_{i}_y"] for i in ['uu', 'ul']],
        [plotLinesInterpolated[f"ghgi_{i}_y"] for i in ['uu', 'ul']],
        corr=plotLinesInterpolated['correlated'],
    )

    plotLinesInterpolated['fscp'] = fscp
    plotLinesInterpolated['fscp_uu'] = fscpu[0]
    plotLinesInterpolated['fscp_ul'] = fscpu[1]

    return plotScatter, plotLinesInterpolated


def __produceFigure(plotScatter: pd.DataFrame, plotLines: pd.DataFrame, config: dict, is_webapp: bool = False, is_uncertainty: bool = False):
    # plot
    fig = make_subplots(
        rows=2,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.025,
        vertical_spacing=0.1,
    )

    # list of subfigs including row and col count for easy access
    subfigs = [(k//2+1, k%2+1, scid) for k, scid in enumerate(config['selected_cases'])]

    # whether to show the box with a legend explaining the cricle annotations
    showAnnotationLegend = False if is_webapp else not is_uncertainty


    # add FSCP traces
    all_traces = __addFSCPTraces(plotScatter, plotLines, config, uncertainity=is_uncertainty)
    hasLegend = []
    for i, j, scid in subfigs:
        for tid, traces in all_traces.items():
            if is_uncertainty and (not config['bgfscp_unc'] and 'NG' not in tid): continue
            tid_techs = '-'.join([fuel.split('-')[0]+'-'+fuel.split('-')[-1] for fuel in tid.split(' to ')])
            if all(fuel in config['selected_cases'][scid] for fuel in tid.split(' to ')):
                for trace in traces:
                    if tid_techs in hasLegend:
                        trace.showlegend = False
                    fig.add_trace(trace, row=i, col=j)
                if tid_techs not in hasLegend:
                    hasLegend.append(tid_techs)


    # compute and plot carbon price tracjetory
    if not is_uncertainty or config['show_cp_unc']:
        cpTrajData = __computeCPTraj(config['co2price_traj']['years'], config['co2price_traj']['values'], config['n_samples'])
        traces = __addCPTraces(cpTrajData, config)
        for trace in traces:
            for i, j, scid in subfigs:
                if i>1 or j>1: trace.showlegend = False
                fig.add_trace(trace, row=i, col=j)


    # zero y line
    for i, j, _ in subfigs:
        fig.add_hline(0.0, line_width=config['global']['lw_thin'], line_color='black', row=i, col=j)


    # add circles on intersects
    if not is_uncertainty:
        __addAnnotations(fig, cpTrajData, plotLines, config)


    # add top and left annotation
    annotationStyling = dict(
        xanchor='center', yanchor='middle', showarrow=False,
        bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white'
    )

    for i in range(2):
        fig.add_annotation(
            x=0.50,
            xref=f"x{str(i+1) if i else ''} domain",
            y=1.0,
            yref='y domain',
            yshift=40,
            text=config['sidelabels']['top'][i],
            **annotationStyling
        )

        fig.add_annotation(
            x=0.0,
            xref='x domain',
            xshift=-100.0 if is_webapp else -150.0,
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
            range=[config['plotting']['t_min'], config['plotting']['t_max']],
        ) for i in range(4)},
        **{f"yaxis{i+1 if i else ''}": dict(
            title=config['labels']['fscp'] if (i+1)%2 else '',
            range=[config['plotting']['fscp_min'], config['plotting']['fscp_max']],
        ) for i in range(4)},
        margin_l=180.0,
    )


    # set legend position
    fig.update_layout(
        legend=dict(
            orientation='h',
            xanchor='left',
            x=0.0,
            yanchor='top',
            y=config['spacings']['legendPosY'] if showAnnotationLegend else -0.1,
        ),
    )


    # add legend for annotations
    if showAnnotationLegend:
        __addAnnotationsLegend(fig, config)

        fig.update_layout(
            **{f"yaxis{i+1 if i else ''}": dict(
                domain=[
                    1.0-config['spacings']['yShareTop'] if i >= 2 else 1.0-(config['spacings']['yShareTop']-config['spacings']['spacingTop'])/2,
                    1.0-(config['spacings']['yShareTop']-config['spacings']['spacingTop'])/2-config['spacings']['spacingTop'] if i >= 2 else 1.0,
                ],
            ) for i in range(4)},
            xaxis5=dict(
                range=[0, 1],
                domain=[0.0, config['spacings']['annotationsLegendWidth']],
                anchor='y5',
                showticklabels=False,
                ticks='',
            ),
            yaxis5=dict(
                range=[0, 1],
                domain=[0.0, config['spacings']['annotationsLegendHeight']],
                anchor='x5',
                showticklabels=False,
                ticks='',
            ),
        )


    return fig


def __addFSCPTraces(plotScatter: pd.DataFrame, plotLines: pd.DataFrame, config: dict, sensitivityNG: bool = False, uncertainity: bool = False):
    traces = {}

    for tid in plotScatter.tid.unique():
        thisTraces = []

        thisScatter = plotScatter.query(f"tid=='{tid}'").reset_index(drop=True)
        thisLine = plotLines.query(f"tid=='{tid}'").reset_index(drop=True)

        # line properties
        fuel_x = thisScatter.iloc[thisScatter.first_valid_index()]['fuel_x']
        fuel_y = thisScatter.iloc[thisScatter.first_valid_index()]['fuel_y']
        name_x = 'NG' if fuel_x.startswith('NG') else config['fuelSpecs'][fuel_x]['shortname']
        name_y = config['fuelSpecs'][fuel_y]['shortname'] + f" ({'Conservative' if fuel_x.endswith('cons') else 'Progressive'})"
        name = f"{name_x}→{name_y}"
        col = config['fscp_colour'][fuel_x.split('-')[-1] + '-' + fuel_y.split('-')[-1]] if 'NG' not in tid else config['fuelSpecs'][fuel_y]['colour']
        isbluegreen = 'NG' not in fuel_x

        if isbluegreen and thisLine.fscp.max() > 2000.0:
            y = thisLine.loc[thisLine.fscp.idxmax(), 'year']
            q = f"year>={y}"
            thisLine = thisLine.query(q)
            thisScatter = thisScatter.query(q)

        # scatter plot
        thisTraces.append(go.Scatter(
            x=thisScatter['year'],
            y=thisScatter['fscp'],
            name=name,
            legendgroup=0 if isbluegreen else 1,
            showlegend=False,
            mode='markers',
            line=dict(color=col, width=config['global']['lw_default']),
            marker=dict(symbol='x-thin', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': col}, ),
            hoverinfo='none',
        ))

        # line plot
        thisTraces.append(go.Scatter(
            x=thisLine['year'],
            y=thisLine['fscp'],
            legendgroup=0 if isbluegreen else 1,
            legendgrouptitle=dict(text=f"<b>{config['legendlabels'][1]}:</b>" if isbluegreen else f"<b>{config['legendlabels'][0]}:</b>"),
            name=name,
            mode='lines',
            line=dict(color=col, width=config['global']['lw_default'], dash='dot' if fuel_x in config['cases_dashed'] or fuel_y in config['cases_dashed'] else 'solid'),
            hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>FSCP: %{{y:.2f}}<extra></extra>",
        ))

        # uncertainity envelope
        if uncertainity:
            x = np.concatenate((thisLine['year'], thisLine['year'][::-1]))
            y = np.concatenate((thisLine['fscp']+thisLine['fscp_uu'], (thisLine['fscp']-thisLine['fscp_ul'])[::-1]))

            thisTraces.append(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(col), .2)),
                fill='toself',
                line=dict(width=config['global']['lw_ultrathin'], color=col),
                showlegend=False,
                hoverinfo="none",
            ))

        traces[tid] = thisTraces

    return traces


def __addAnnotations(fig: go.Figure, cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, config: dict):
    for i, j, scid in [(k//2+1, k%2+1, scid) for k, scid in enumerate(config['selected_cases'])]:
        points = __calcPoints(cpTrajData, plotLines, config['selected_cases'][scid], config)
        data = points.query(f"delta < 5.0")

        for _, row in data.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[row.year],
                    y=[row.fscp],
                    text=[int(row.label)],
                    mode='markers+text',
                    marker=dict(symbol='circle-open', size=config['global']['highlight_marker'], line={'width': config['global']['lw_thin']}, color=row.colour),
                    textfont_color=row.colour,
                    textposition='bottom center',
                    showlegend=False,
                    hovertemplate = f"<b>Milestone {int(row.label)}:</b> {config['annotationTexts'][f'point{int(row.label)}']}<br>Time: %{{x:.2f}}<br>FSCP: %{{y:.2f}}<extra></extra>",
                ),
                row=i,
                col=j,
            )


def __calcPoints(cpTrajData: pd.DataFrame, plotLines: pd.DataFrame, fuels: list, config: dict) -> dict:
    points = []

    types = ['NG', 'BLUE', 'GREEN']
    groupedFuels = {t: [f for f in fuels if not plotLines.query(f"(fuel_x=='{f}' and type_x=='{t}') or (fuel_y=='{f}' and type_y=='{t}')").empty] for t in types}

    for fuelRef, fuelBlue, fuelGreen in [(r,b,g) for r in groupedFuels['NG'] for b in groupedFuels['BLUE'] for g in groupedFuels['GREEN']]:
        dropCols = ['tid', 'type_x', 'type_y', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']
        greenLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)
        blueLine = plotLines.query(f"fuel_x=='{fuelRef}' & fuel_y=='{fuelBlue}'").drop(columns=dropCols).reset_index(drop=True)
        redLine = plotLines.query(f"fuel_x=='{fuelBlue}' & fuel_y=='{fuelGreen}'").drop(columns=dropCols).reset_index(drop=True)

        purpleLine = cpTrajData.drop(columns=['name', 'CP_u', 'CP_l'])

        # marker 4
        diffLines = pd.merge(blueLine, greenLine, on=['year'], suffixes=('', '_right'))
        diffLines['delta'] = (diffLines['fscp'] - diffLines['fscp_right']).abs()
        points.append(diffLines.nsmallest(1, 'delta').drop(columns=['fscp_right']).head(1).assign(label=4, colour='black'))

        if fuelGreen in config['cases_dashed'] or fuelBlue in config['cases_dashed']:
            continue

        # markers 1-3
        for i, line in enumerate([blueLine, greenLine, redLine]):
            fuel_x = line.fuel_x.iloc[1]
            fuel_y = line.fuel_y.iloc[1]
            col = config['fscp_colour'][fuel_x.split('-')[-1] + '-' + fuel_y.split('-')[-1]] if 'NG' not in fuel_x else config['fuelSpecs'][fuel_y]['colour']
            diffLines = pd.merge(line, purpleLine, on=['year'])
            diffLines['delta'] = (diffLines['fscp'] - diffLines['CP']).abs()
            points.append(diffLines.nsmallest(1, 'delta').drop(columns=['CP']).head(1).assign(label=i+1, colour=col))

        # marker 5
        redLine['abs'] = redLine['fscp'].abs()
        points.append(redLine.nsmallest(1, 'abs').assign(delta=lambda r: r.fscp).head(1).assign(label=5, colour='black'))

    return pd.concat(points)


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
    xmargin = 0.01
    ymargin = 0.05
    lineheight = 0.2
    spacing = 0.02

    for i in range(2):
        t = config['annotationTexts'][f"heading{i+1}"]
        fig.add_annotation(
            text=f"<b>{t}:</b>",
            align='left',
            xanchor='left',
            x=xmargin,
            yanchor='top',
            y=(0.5 if i else 1.0) - ymargin,
            xref='x5 domain',
            yref='y5 domain',
            showarrow=False,
        )

    labels = [
        [
            i+1,
            (i%2 + (2 if i==4 else 0)) * 0.33 * 1.13 + 2*xmargin,
            (1.0 if i<2 else 0.5) - ymargin - lineheight,
        ]
        for i in range(5)
    ]

    psi, psx, psy = zip(*labels)
    fig.add_trace(
        go.Scatter(
            x=psx,
            y=psy,
            text=psi,
            mode='markers+text',
            marker=dict(symbol='circle-open', size=config['global']['highlight_marker'], line={'width': config['global']['lw_thin']}, color='black'),
            textposition='bottom center',
            showlegend=False,
            hoverinfo='skip',
            xaxis='x5',
            yaxis='y5',
        )
    )

    for i, x, y in labels:
        t = config['annotationTexts'][f"point{i}"]
        fig.add_annotation(
            text=f"{t}",
            align='left',
            xanchor='left',
            x=x+spacing,
            yanchor='top',
            y=y+0.05,
            xref='x5 domain',
            yref='y5 domain',
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
        'year': [float(y) for y in years],
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
        legendgroup=3,
        legendgrouptitle=dict(text=f"<b>{config['legendlabels'][2]}</b>:"),
        mode='lines',
        x=cpTrajData['year'],
        y=cpTrajData['CP'],
        line_color=colour,
        line_width=config['global']['lw_thin'],
        showlegend=True,
        hovertemplate=f"<b>{name}</b><br>Time: %{{x:.2f}}<br>Carbon price: %{{y:.2f}}<extra></extra>",
    ))

    data_x = cpTrajData['year']
    data_yu = cpTrajData['CP'] + cpTrajData['CP_u']
    data_yl = cpTrajData['CP'] - cpTrajData['CP_l']

    errorBand = go.Scatter(
        name='Uncertainty Range',
        legendgroup=3,
        x=pd.concat([data_x, data_x[::-1]], ignore_index=True),
        y=pd.concat([data_yl, data_yu[::-1]], ignore_index=True),
        mode='lines',
        marker=dict(color=colour),
        fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(colour))),
        fill='toself',
        line=dict(width=config['global']['lw_ultrathin']),
        showlegend=False,
        hoverinfo='none'
    )
    traces.append(errorBand)

    return traces
