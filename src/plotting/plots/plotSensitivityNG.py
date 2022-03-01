from string import ascii_lowercase

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.plotting.plots.plotHeatmap import __produceFigure, __selectPlotData
from src.plotting.plots.plotOverTime import __selectPlotFSCPs, __addFSCPTraces, __computeCPTraj, __addCPTraces
from src.timeit import timeit


@timeit
def plotSensitivityNG(fuelData: pd.DataFrame, FSCPData: pd.DataFrame, fullParams: pd.DataFrame, config: dict):
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=ascii_lowercase,
        horizontal_spacing=0.1,
        vertical_spacing=0.05,
    )


    # plots to reproduce
    typeHeatmap = 'left'
    typeOverTime = 'refFuelTop'


    # updated plotFSCP and FSCPs for ii)
    fuelDataII = fuelData.copy(deep=True)
    fuelDataII[['cost__fuel_cost']] = fuelDataII[['cost__fuel_cost']].fillna(value=0.0)
    p_ng = fullParams.query(f"name=='cost_ng_price'").filter(items=['year', 'value']).rename(columns={'value': 'p_ng'}).assign(p_ng_new=lambda x: x['p_ng'] + config['addNGPrice'])
    fuelDataII = fuelDataII.merge(p_ng, on=['year']).assign(cost=lambda x: x['cost'] + x['cost__fuel_cost'] * (x['p_ng_new'] / x['p_ng'] - 1.0))


    # updated plotFSCP and FSCPs for iii)
    fuelDataIII = fuelData.copy(deep=True)
    fuelDataIII[['cost__elec_cost']] = fuelDataIII[['cost__elec_cost']].fillna(value=0.0)
    p_el = fullParams.query(f"name=='cost_green_elec_RE'").filter(items=['year', 'value']).rename(columns={'value': 'p_el'}).assign(p_el_new=lambda x: x['p_el'] + config['addElPrice'])
    fuelDataIII = fuelDataIII.merge(p_el, on=['year']).assign(cost=lambda x: x['cost'] + x['cost__elec_cost']*(x['p_el_new']/x['p_el']-1.0))


    # produce heatmap subplots
    cfg = {**config['plotHeatmap'], **{t: {**config[t]} for t in ['names', 'colours', 'global']}}

    for j, fData in [(1, fuelData,),
                     (2, fuelDataII,),
                     (3, fuelDataIII,),]:
        plotData, refData = __selectPlotData(fData, config['plotHeatmap']['refFuel'][typeHeatmap], config['plotHeatmap']['refYear'][typeHeatmap], config['plotHeatmap']['showFuels'])

        # determine y-axis plot range
        shift = 0.1
        ylow = refData.cost - shift * (config['plotHeatmap']['plotting']['cost_max'] - refData.cost)

        fig = __produceFigure(fig, plotData, refData, ylow, cfg, typeHeatmap, row=j, col=1)


    # remove manual margins and heatmap colorbar
    fig.update_layout(
        margin_t=None,
        margin_r=None,
    )
    for trace in fig['data']:
        if isinstance(trace, go.Heatmap):
            trace.update(showscale=False)


    # add FSCP traces for heating and compute and plot carbon price tracjetory
    cfg = {**config['plotOverTime'], **{t: {**config[t]} for t in ['names', 'colours', 'global']}}

    cpTrajData = __computeCPTraj(config['plotOverTime']['co2price_traj']['years'], config['plotOverTime']['co2price_traj']['values'], config['plotOverTime']['n_samples'])
    cpTraces = __addCPTraces(cpTrajData, cfg)

    for j, fData in [(1, fuelData,),
                     (2, fuelDataII,),
                     (3, fuelDataIII,),]:

        # obtain default plotting data
        FSCPsCols, plotFSCP, plotLines = __selectPlotFSCPs(calcFSCPs(fData), config['plotOverTime']['showFSCPs'], config['plotOverTime'][typeOverTime], config['plotOverTime']['n_samples'])

        if j == 2:
        #    plotFSCP = plotFSCP.query("fuel_x!='blue LEB' | fuel_y!='green pure RE'")
            print(plotFSCP.query("fuel_x=='blue LEB' & fuel_y=='green RE'"))

        traces = __addFSCPTraces(plotFSCP, plotLines, len(FSCPsCols), config['plotOverTime'][typeOverTime], cfg, sensitivityNG=j==2)
        for id, trace in traces:
            if 2 in FSCPsCols[id]:
                fig.add_trace(trace, row=j, col=2)

        for trace in cpTraces:
            fig.add_trace(trace, row=j, col=2)
        fig.add_hline(0.0, line_width=config['global']['lw_thin'], line_color='black', row=j, col=2)


    # set ranges and titles for axes
    for axis in ['xaxis2', 'yaxis2', 'xaxis4', 'yaxis4', 'xaxis6', 'yaxis6']:
        otherAxis = axis[:-1] + str(int(axis[-1])-1)
        if otherAxis.endswith('1'): otherAxis = otherAxis[:-1]

        fig.update_layout({
            axis: dict(
                title=config['plotOverTime']['labels']['time'],
                range=[config['plotOverTime']['plotting']['t_min'], config['plotOverTime']['plotting']['t_max']],
                domain=[0.525, 1.0],
            ) if axis.startswith('x') else dict(
                title=config['plotOverTime']['labels']['fscp'],
                range=[config['plotOverTime']['plotting']['fscp_min'], config['plotOverTime']['plotting']['fscp_max']],
                domain=fig['layout'][otherAxis]['domain'],
                anchor=axis.replace('y', 'x').replace('axis', '')
            ),
        })


    # remove annotations
    fig['layout']['annotations'] = fig['layout']['annotations'][:6]
    fig.update_layout(showlegend=False)


    # styling figure
    __styling(fig)


    return {'fig7': fig}


def __styling(fig: go.Figure):
    # update axis styling
    for axis in ['xaxis', 'yaxis', 'xaxis2', 'yaxis2', 'xaxis3', 'yaxis3', 'xaxis4', 'yaxis4', 'xaxis5', 'yaxis5', 'xaxis6', 'yaxis6']:
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


    # set ranges and titles for axes 3 till 6
    for axis in ['xaxis3', 'yaxis3', 'xaxis5', 'yaxis5']:
        fig['layout'][axis]['matches'] = axis[0]
        if axis.startswith('x'):
            fig['layout'][axis]['title'] = fig['layout']['xaxis']['title']
        else:
            fig['layout'][axis]['title'] = fig['layout']['yaxis']['title']


    for axis in ['xaxis4', 'yaxis4', 'xaxis6', 'yaxis6']:
        fig['layout'][axis]['matches'] = axis[0] + '2'
        if axis.startswith('x'):
            fig['layout'][axis]['title'] = fig['layout']['xaxis2']['title']
        else:
            fig['layout'][axis]['title'] = fig['layout']['yaxis2']['title']


    # update figure background colour and font colour and type
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 1.0)',
        plot_bgcolor='rgba(255, 255, 255, 0.0)',
        font_color='black',
        font_family='Helvetica',
    )


    # update subplot labels
    for i, annotation in enumerate(fig['layout']['annotations'][:6]):
        # make bold
        annotation['text'] = "<b>{0}</b>".format(annotation['text'])

        # reference axes and anchors
        annotation['xref'] = (f"x{i+1}" if i else 'x') + ' domain'
        annotation['yref'] = (f"y{i+1}" if i else 'y') + ' domain'
        annotation['xanchor'] = 'left'
        annotation['yanchor'] = 'bottom'

        # position
        annotation['x'] = 0.0
        annotation['y'] = 1.05
