from string import ascii_lowercase

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.config_load import steel_data
from src.timeit import timeit


@timeit
def plot4(fuelData: pd.DataFrame, fuelDataSteel: pd.DataFrame, config: dict):

    figs = {}
    for subFigName, type, fData in [('a', 'left', fuelData), ('b', 'right', fuelDataSteel)]:
        plotData, refData = __selectPlotData(fData, config['refFuel'][type], config['refYear'][type], config['showFuels'])

        # determine y-axis plot range
        if type == 'left':
            shift = 0.1
            ylow = refData.cost - shift * (config['plotting']['cost_max'] - refData.cost)

        # produce figures
        fig = __produceFigure(plotData, refData, ylow, config, type)

        # styling figure
        __styling(fig)

        figs.update({f"fig4{subFigName}": fig})

    return figs


def __selectPlotData(fuelsData: pd.DataFrame, refFuel: str, refYear: int, showFuels: list):
    plotData = fuelsData.query('fuel in @showFuels')
    refData = fuelsData.query(f"fuel=='{refFuel}' & year=={refYear}").iloc[0]

    return plotData, refData


def __produceFigure(plotData: pd.DataFrame, refData: pd.Series, ylow: float, config: dict, type: str):
    # define plotly figure
    fig = go.Figure()


    # subplot labels
    fig.add_annotation(
        showarrow=False,
        text=f"<b>{'a' if type=='left' else 'b'}</b>",
        x=0.0,
        xanchor='left',
        xref='paper',
        y=1.15,
        yanchor='top',
        yref='paper',
    )


    # left and right settings
    if type == 'left':
        thickLines = [
            {'size': 100, 'start': 100, 'end': 600},
            {'size': 250, 'start': 750, 'end': 1000},
            {'size': 300, 'start': 1200, 'end': 1500},
        ]

        plotConf = {
            'ghgi_min': 0.0,
            'ghgi_max': config['plotting']['ghgi_max'],
            'cost_min': 0.0,
            'cost_max': config['plotting']['cost_max'],
            'n_samples': config['plotting']['n_samples'],
        }
    else:
        thickLines = [
            {'size': 50, 'start': 50, 'end': 200},
        ]

        plotConf = {
            'ghgi_min': steel_data['other_ghgi'],
            'ghgi_max': config['plotting']['ghgi_max'] * steel_data['h2_demand'] + steel_data['other_ghgi'],
            'cost_min': steel_data['other_cost'],
            'cost_max': config['plotting']['cost_max'] * steel_data['h2_demand'] + steel_data['other_cost'],
            'n_samples': config['plotting']['n_samples'],
        }

        fig.add_trace(go.Scatter(x=[-999.0], y=[-999.0], showlegend=False))


    # add line traces
    traces = __addLineTraces(plotData, config['showFuels'], config)
    for trace in traces:
        fig.add_trace(trace)
        if type == 'right':
            fig['data'][-1]['xaxis'] = 'x2'
            fig['data'][-1]['yaxis'] = 'y2'


    # add FSCP traces
    traces = __addFSCPTraces(refData, thickLines, plotConf, config['global']['lw_thin'], config['global']['lw_ultrathin'], type=='left')
    for trace in traces:
        fig.add_trace(trace)
        if type == 'right':
            fig['data'][-1]['xaxis'] = 'x2'
            fig['data'][-1]['yaxis'] = 'y2'
    #fig.add_hline(refData.cost, line_width=4, line_dash="dash", line_color='black', row=1, col=1)


    # set plotting ranges
    fig.update_layout(
        xaxis=dict(
            title=config['labels']['ghgi'],
            range=[0.0, config['plotting']['ghgi_max']*1000]
        ),
        yaxis=dict(
            title=config['labels']['cost'],
            range=[ylow, config['plotting']['cost_max']]
        ),
        xaxis2=dict(
            title=config['labels']['ghgiSteel'],
            range=[steel_data['other_ghgi']*1000, (config['plotting']['ghgi_max'] * steel_data['h2_demand'] + steel_data['other_ghgi'])*1000],
            overlaying='x2',
            anchor='y2',
            side='top',
            ticks='outside',
        ) if type=='right' else None,
        yaxis2=dict(
            title=config['labels']['costSteel'],
            range=[ylow*steel_data['h2_demand'] + steel_data['other_cost'], config['plotting']['cost_max']*steel_data['h2_demand'] + steel_data['other_cost']],
            overlaying='y2',
            anchor='x2',
            side='right',
            ticks='outside',
        ) if type=='right' else None,
        margin_t=160.0,
        margin_r=200.0,
    )


    # add text annotations explaining figure content
    annotationStylingA = dict(xanchor='center', yanchor='bottom', showarrow=False,
                              bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

    application = config['annotationLabels'][type]
    fig.add_annotation(
        x=0.50,
        xref='x domain',
        y=1.15,
        yref='y domain',
        text=application,
        **annotationStylingA
    )

    annotationStylingB = dict(xanchor='left', yanchor='top', showarrow=False)
    if type == 'left':
        fig.add_annotation(x=0.01*config['plotting']['ghgi_max']*1000,
                           y=refData.cost,
                           xref="x", yref="y", text='Price of natural gas', **annotationStylingB)
    else:
        # fig.add_annotation(x=0.01*config['plotting']['ghgi_max']*1000,
        #                   y=refDataLeft.cost,
        #                   xref="x2", yref="y2", text='Direct cost of conventional steel (BF-BOF)', **annotationStylingB)
        pass


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


        # points and lines
        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            text=thisData.year,
            textposition='top left',
            textfont=dict(color=col),
            name=name,
            legendgroup=fuel,
            showlegend=False,
            mode="markers+text",
            line=dict(color=col),
            marker_size=config['global']['highlight_marker_sm'],
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity: %{{x:.2f}}<br>Direct cost: %{{y:.2f}}<extra></extra>"
        ))

        traces.append(go.Scatter(
            x=thisData.ghgi*1000,
            y=thisData.cost,
            name=name,
            legendgroup=fuel,
            showlegend=True,
            line=dict(color=col, width=config['global']['lw_default'], dash='dot' if dashed else 'solid'),
            mode='lines',
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
            title='<i>FSCP</i><sub>Fossil→H<sub>2</sub></sub>',
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


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='bottom',
            y=0.00,
            xanchor='right',
            x=1.00,
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
