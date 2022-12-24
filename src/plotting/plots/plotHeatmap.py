import numpy as np
import pandas as pd

import plotly.graph_objects as go

from src.timeit import timeit


@timeit
def plotHeatmap(fuelData: pd.DataFrame, config: dict, subfigs_needed: list, is_webapp: bool = False):
    ret = {}
    for sub, type in [('a', 'left'), ('b', 'right')]:
        subfigName = f"fig4{sub}"


        # check if plotting is needed
        if subfigName not in subfigs_needed:
            ret.update({subfigName: None})
            continue


        # select data
        plotData, refData = __selectPlotData(fuelData, config['refFuel'][type], config['refYear'][type], config['showFuels'][type], config['showYears'])


        # define plotly figure
        fig = go.Figure()


        # produce figures
        fig = __produceFigure(fig, plotData, refData, config, type)


        ret.update({subfigName: fig})

    return ret


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, refYear: int, showFuels: list, showYears: list):
    plotData = fuelsData.query('fuel in @showFuels and year in @showYears')
    refData = fuelsData.query(f"fuel=='{refFuel}' & year=={refYear}").iloc[0]


    return plotData, refData


def __produceFigure(fig: go.Figure, plotData: pd.DataFrame, refData: pd.Series, config: dict, type: str, row=None, col=None):
    argsRowCol = dict(row=row, col=col) if row is not None and col is not None else dict()

    plotConf = {
        'ghgi_min': 0.0,
        'ghgi_max': config['plotting']['ghgi_max'],
        'cost_min': 0.0,
        'cost_max': config['plotting']['cost_max'],
        'n_samples': config['plotting']['n_samples'],
    }


    # add line traces
    traces = __addLineTraces(plotData, config)
    for trace in traces:
        fig.add_trace(trace, **argsRowCol)


    # add FSCP traces
    traces = __addFSCPTraces(refData, config['thickLines'][type], plotConf, config['global']['lw_thin'], config['global']['lw_ultrathin'], type=='right')
    for trace in traces:
        fig.add_trace(trace, **argsRowCol)


    # determine y-axis plot range
    shift = 0.1
    ylow = refData.cost - shift * (config['plotting']['cost_max'] - refData.cost)


    # set plotting ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['ghgi'],
            range=[0.0, config['plotting']['ghgi_max']*1000],
        ),
        yaxis=dict(
            title=config['labels']['cost'],
            range=[ylow, config['plotting']['cost_max']],
        ),
        margin_t=160.0,
        margin_r=200.0,
    )


    # add text annotations explaining figure content
    annotationStylingA = dict(xanchor='center', yanchor='bottom', showarrow=False,
                              bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

    topLabel = config['annotationLabels'][type]
    fig.add_annotation(
        x=0.50,
        xref='x domain',
        y=1.0,
        yref='y domain',
        yshift=20.0,
        text=topLabel,
        **annotationStylingA,
        **argsRowCol,
    )

    annotationStylingB = dict(xanchor='left', yanchor='top', showarrow=False)
    fig.add_annotation(
        x=0.01*config['plotting']['ghgi_max']*1000,
        y=refData.cost,
        xref='x', yref='y', text='Price of natural gas',
        **annotationStylingB,
        **argsRowCol,
    )


    # set legend position
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=-0.2,
            xanchor='left',
            x=0.0,
        ),
    )


    return fig


def __addLineTraces(plotData: pd.DataFrame, config: dict):
    traces = []
    hasLegend = []

    for fuel in plotData.fuel.unique():
        # line properties
        descs = [
            'progressive' if 'prog' in fuel else 'conservative',
            'low supply-chain CO<sub>2</sub>' if fuel.endswith('lowscco2') else None,
            '75-to-100% RE share' if 'ME' in fuel else None,
        ]
        name = config['fuelSpecs'][fuel]['name'].split(' (')[0] + f" ({', '.join([d for d in descs if d])})"
        col = config['fuelSpecs'][fuel]['colour']
        tech = fuel
        dashed = any(t in fuel for t in config['tokensDashed'])


        # data
        thisData = plotData.query(f"fuel=='{fuel}'")


        # points and lines
        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            text=thisData.year if not fuel.endswith('lowscco2') else None,
            textposition='top left' if 'pess' in fuel else 'bottom right',
            textfont=dict(color=col),
            name=name,
            legendgroup=fuel,
            showlegend=False,
            mode='markers+text',# if tech not in hasLegend else 'markers',
            line=dict(color=col),
            marker_size=config['global']['highlight_marker_sm'],
            hoverinfo='skip',
        ))

        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            name=name,
            legendgroup=tech,
            showlegend=tech not in hasLegend,
            line=dict(color=col, width=config['global']['lw_default'], dash='dot' if dashed else 'solid'),
            mode='lines',
            hoverinfo='skip',
        ))

        if tech not in hasLegend:
            hasLegend.append(tech)


        # hover template
        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            error_x=dict(type='data', array=thisData.ghgi_uu*1000, arrayminus=thisData.ghgi_ul*1000, thickness=0.0),
            error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=0.0),
            line_color=col,
            showlegend=False,
            mode='lines',
            line_width=0.000001,
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b><br>Year: %{{customdata}}<br>Carbon intensity: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>Direct cost: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))


        # error bars
        thisData = thisData.query(f"year==[2025,2030,2040,2050]")
        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            error_x=dict(type='data', array=thisData.ghgi_uu*1000, arrayminus=thisData.ghgi_ul*1000, thickness=config['global']['lw_thin']),
            error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=config['global']['lw_thin']),
            line_color=col,
            marker_size=0.000001,
            showlegend=False,
            mode='markers',
            customdata=thisData.year,
            hoverinfo='skip',
        ))


    return traces


def __addFSCPTraces(refData: pd.Series, thickLines: list, plotConf: dict, lw_thin: float, lw_ultrathin: float, showscale: bool):
    traces = []

    ghgi_samples = np.linspace(plotConf['ghgi_min'], plotConf['ghgi_max'], plotConf['n_samples'])
    cost_samples = np.linspace(plotConf['cost_min'], plotConf['cost_max'], plotConf['n_samples'])
    ghgi_v, cost_v = np.meshgrid(ghgi_samples, cost_samples)

    ghgi_ref = refData.ghgi
    cost_ref = refData.cost

    fscp = (cost_v - cost_ref)/(ghgi_ref - ghgi_v)

    # heatmap
    tickvals = [100*i for i in range(6)]
    ticktext = [str(v) for v in tickvals]
    ticktext[-1] = '> 500'
    traces.append(go.Heatmap(
        x=ghgi_samples*1000, y=cost_samples, z=fscp,
        zsmooth='best', hoverinfo='skip',
        zmin=0.0, zmax=500.0,
        colorscale=[
            [0.0, '#c6dbef'],
            [1.0, '#f7bba1'],
        ],
        colorbar=dict(
            x=1.05,
            y=0.25,
            len=0.5,
            title='<i>FSCP</i><sub>NG→H<sub>2</sub></sub>',
            titleside='top',
            tickvals=tickvals,
            ticktext=ticktext,
        ),
        showscale=showscale,
    ))

    # thin lines every 50
    traces.append(go.Contour(x=ghgi_samples*1000, y=cost_samples, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             line_width=lw_ultrathin,
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
                             line=dict(width=lw_thin, dash='dash')))

    # thick lines
    for kwargs in thickLines:
        traces.append(go.Contour(
            x=ghgi_samples*1000, y=cost_samples, z=fscp,
            showscale=False, contours_coloring='lines', hoverinfo='skip',
            colorscale=[
                [0.0, '#000000'],
                [1.0, '#000000'],
            ],
            line_width=lw_thin,
            contours=dict(
                showlabels=True,
                labelfont=dict(
                    color='black',
                ),
                **kwargs,
            )))


    return traces
