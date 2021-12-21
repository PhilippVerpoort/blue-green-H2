import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.calc_ci import getCIParamsBlue, getCIParamsGreen, getCIGreen, getCIBlue
from src.data.calc_fuels import getCurrentAsDict


def plotFig5(fuelSpecs: dict, fuelData: pd.DataFrame, fullParams: pd.DataFrame, fuels: dict,
             plotConfig: dict, scenario_name = "", export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # produce figure
    fig = __produceFigure(fuelData, fullParams, fuels, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig5" + ("_"+scenario_name if scenario_name else "") + ".png",
                        width=1550, height=700)

    return fig


def __produceFigure(fuelData: pd.DataFrame, fullParams: pd.DataFrame, fuels: dict, config: dict):
    # plot
    fig = make_subplots(rows=2,
                        cols=4,
                        specs=[
                            [{"rowspan": 2, "colspan": 2}, None, {}, {}],
                            [None, None, {}, {}],
                        ],
                        subplot_titles=tuple(t for t in config['subplot_titles']),
                        horizontal_spacing=0.02,
                        vertical_spacing=config['vertical_spacing'],
                        shared_yaxes=True)
    rowcol_mapping = [
        dict(row=1, col=1),
        dict(row=1, col=3),
        dict(row=1, col=4),
        dict(row=2, col=3),
        dict(row=2, col=4),
    ]

    calcedRanges = {}


    # get colour scale config
    zmin, zmax, colourscale = __getColourScale(config)

    # add FSCP traces
    traces = __addFSCPContours(config, zmin, zmax, colourscale)
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[0])

    # add scatter curves
    traces = __addFSCPScatterCurves(fuelData, config)
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[0])

    # add FSCP traces in subplots
    fuelGreen = fuels[config['fuelGreen']]

    fuelBlue = fuels[config['fuelBlueLeft']]
    xmin, xmax = config['plotting']['xaxis2_min'], config['plotting']['xaxis2_max']
    traces, calcedRanges['xaxis7'], calcedRanges['xaxis12'] = __addFSCPSubplotContoursTop(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot2"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[1])

    fuelBlue = fuels[config['fuelBlueRight']]
    xmin, xmax = config['plotting']['xaxis3_min'], config['plotting']['xaxis3_max']
    traces, calcedRanges['xaxis8'], calcedRanges['xaxis13'] = __addFSCPSubplotContoursTop(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot3"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[2])

    fuelBlue = fuels[config['fuelBlueLeft']]
    xmin, xmax = config['plotting']['xaxis4_min'], config['plotting']['xaxis4_max']
    traces, calcedRanges['xaxis9'], calcedRanges['xaxis14'], xvline = __addFSCPSubplotContoursBottom(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot4"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[3])
    fig.add_vline(x=xvline*100, line_width=3, line_color="black", **rowcol_mapping[3])

    fuelBlue = fuels[config['fuelBlueRight']]
    xmin, xmax = config['plotting']['xaxis5_min'], config['plotting']['xaxis5_max']
    traces, calcedRanges['xaxis10'], calcedRanges['xaxis15'], xvline = __addFSCPSubplotContoursBottom(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot5"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[4])
    fig.add_vline(x=xvline*100, line_width=5, line_color="black", **rowcol_mapping[4])


    # add mock traces to make additional x axes show
    fig.add_trace(go.Scatter(x=[1.0], y=[100], showlegend=False), row=1, col=3)
    fig['data'][-1]['xaxis'] = 'x7'
    fig.add_trace(go.Scatter(x=[2.0], y=[100], showlegend=False), row=1, col=4)
    fig['data'][-1]['xaxis'] = 'x8'
    #fig.add_trace(go.Scatter(x=[3.0], y=[100], showlegend=False), row=2, col=3)
    #fig['data'][-1]['xaxis'] = 'x9'
    #fig.add_trace(go.Scatter(x=[4.0], y=[100], showlegend=False), row=2, col=4)
    #fig['data'][-1]['xaxis'] = 'x10'
    fig.add_trace(go.Scatter(x=[5.0], y=[100], showlegend=False), row=1, col=3)
    fig['data'][-1]['xaxis'] = 'x12'
    fig.add_trace(go.Scatter(x=[6.0], y=[100], showlegend=False), row=1, col=4)
    fig['data'][-1]['xaxis'] = 'x13'
    fig.add_trace(go.Scatter(x=[7.0], y=[100], showlegend=False), row=2, col=3)
    fig['data'][-1]['xaxis'] = 'x14'
    fig.add_trace(go.Scatter(x=[8.0], y=[100], showlegend=False), row=2, col=4)
    fig['data'][-1]['xaxis'] = 'x15'


    # set y axes titles and ranges
    fig.update_yaxes(title="", range=[config['plotting']['yaxis2_min'], config['plotting']['yaxis2_max']])
    fig.update_yaxes(title=config['labels']['yaxis1'], range=[config['plotting']['yaxis1_min'], config['plotting']['yaxis1_max']], ticks='outside', row=1, col=1)
    fig.update_yaxes(ticks='outside', row=1, col=3)
    fig.update_yaxes(ticks='outside', row=2, col=3)


    # set x axes titles and ranges
    newAxes = __getXAxesStyle(calcedRanges, config)
    fig.update_layout(**newAxes)


    # legend settings
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="center",
            x=0.165,
            bgcolor = 'rgba(255,255,255,0.6)',
            font = dict(size = 12),
        ),
    )


    # move title annotations
    for i, annotation in enumerate(fig['layout']['annotations']):
        x_pos, y_pos = config['subplot_title_positions'][i]
        annotation['x'] = x_pos
        annotation['y'] = y_pos
        annotation['text'] = "<b>{0}</b>".format(annotation['text'])

    return fig


def __addFSCPContours(config: dict, zmin: float, zmax: float, colourscale: list):
    traces = []

    delta_ci = np.linspace(config['plotting'][f"xaxis1_min"], config['plotting'][f"xaxis1_max"], config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting'][f"yaxis1_min"], config['plotting'][f"yaxis1_max"], config['plotting']['n_samples'])
    delta_ci_v, delta_cost_v = np.meshgrid(delta_ci, delta_cost)
    fscp = delta_cost_v / delta_ci_v

    traces.append(go.Heatmap(x=delta_ci * 1000, y=delta_cost, z=fscp,
                             zsmooth='best', showscale=True, hoverinfo='skip',
                             zmin=zmin, zmax=zmax,
                             colorscale=colourscale,
                             colorbar=dict(
                                 x=1.0,
                                 y=0.4,
                                 len=0.8,
                                 title='FSCP',
                                 titleside='top',
                             )))

    traces.append(go.Contour(x=delta_ci * 1000, y=delta_cost, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=True,
                                 labelformat='.4',
                                 start=zmin,
                                 end=zmax,
                                 size=config['linedensity'][f"plot1"],
                             )))

    return traces


def __addFSCPScatterCurves(fuelData: pd.DataFrame, config: dict):
    traces = []

    for fuel_x in [config['fuelBlueLeft'], config['fuelBlueRight']]:
        fuel_y = config['fuelGreen']
        thisData = __convertFuelData(fuelData, fuel_x, fuel_y)

        name = f"FSCP {config['names'][fuel_x]} to {config['names'][fuel_y]}"

        traces.append(go.Scatter(x=thisData.delta_ci * 1000, y=thisData.delta_cost,
            error_x=dict(type='data', array=thisData.delta_ci_u*1000),
            error_y=dict(type='data', array=thisData.delta_cost_u),
            name=name,
            legendgroup=f"{fuel_x}__{fuel_y}",
            line=dict(color=config['fscp_colours'][f"{fuel_x} to {fuel_y}"]),
            mode='lines+markers',
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity difference: %{{x:.2f}}±%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>",
        ))

    return traces


def __addFSCPSubplotContoursTop(fullParams: pd.DataFrame, fuelGreen: dict, fuelBlue: dict, xmin: float, xmax: float, config: dict, zmin: float, zmax: float, colourscale: list, linedensity: float):
    traces = []


    # define data for plot grid
    leakage = np.linspace(xmin, xmax, config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting']['yaxis1_min'], config['plotting']['yaxis1_max'], config['plotting']['n_samples'])

    # calculate CI data from params
    gwp = 'gwp100'
    gwpOther = 'gwp20' if gwp == 'gwp100' else 'gwp100'

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getCIParamsBlue(currentParams, fuelBlue, gwp)
    pGreen = getCIParamsGreen(currentParams, fuelGreen, gwp)

    # calculate FSCPs for grid
    leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
    pBlue['mlr'] = leakage_v
    CIBlue, CIGreen = __getCIs(pBlue, pGreen)
    fscp = delta_cost_v / (CIBlue - CIGreen)

    # add traces
    traces.append(go.Heatmap(x=leakage * 100, y=delta_cost, z=fscp,
                             zsmooth='best', showscale=False, hoverinfo='skip',
                             zmin=zmin, zmax=zmax,
                             colorscale=colourscale,
                             colorbar=dict(
                                 x=1.0,
                                 y=0.5,
                                 len=1.0,
                                 title='FSCP',
                                 titleside='top',
                             )))

    traces.append(go.Contour(x=leakage * 100, y=delta_cost, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=True,
                                 start=zmin,
                                 end=zmax,
                                 size=linedensity,
                             )))

    # determine other xaxis ranges
    pBlue = getCIParamsBlue(currentParams, fuelBlue, gwp)
    pBlueOther = getCIParamsBlue(currentParams, fuelBlue, gwpOther)
    # ci0_1 + p_1 * cim_1 = ci0_2 + p_2 * cim_2
    # p_2 = (p_1*cim_1+ci0_1-ci0_2)/cim_2
    range2  = [(x*pBlue['mci']+pBlue['b']-pBlueOther['b']) / pBlueOther['mci']
               for x in [xmin, xmax]]
    range3 = [CIBlue[0][0], CIBlue[0][-1]]

    return traces, range2, range3


def __addFSCPSubplotContoursBottom(fullParams: pd.DataFrame, fuelGreen: dict, fuelBlue: dict, xmin: float, xmax: float,
                                   config: dict, zmin: float, zmax: float, colourscale: list, linedensity: float):
    traces = []

    # turn this on to set methane leakage to zero in subplots (d) and (e)
    #fullParams = fullParams.copy()
    #fullParams.loc[fullParams['name'] == 'ci_ng_methaneleakage', 'value'] = 0.0

    # define data for plot grid
    renewablesShare = np.linspace(xmin, xmax, config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting'][f"yaxis1_min"], config['plotting'][f"yaxis1_max"], config['plotting']['n_samples'])

    # calculate CI data from params
    gwp = 'gwp100'
    gwpOther = 'gwp20' if gwp == 'gwp100' else 'gwp100'

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getCIParamsBlue(currentParams, fuelBlue, gwp)
    pGreen = getCIParamsGreen(currentParams, fuelGreen, gwp)

    # carbon intensity of grid electricity (needs to be obtained from data file in future after green CI has been tidied up)
    gridCI = 0.397
    gridCIOther = 0.434

    # calculate xvline
    # 0 = CIGreen(x) - CIBlue =  CIGreen(1) + eff* ((x-1) * eci + (1-x) * gci) - CIBlue
    # ((CIBlue - CIGreen)/eff + eci - gci) / (eci - gci) = x
    CIBlue, CIGreen = __getCIs(pBlue, pGreen)
    xvline = (CIBlue - CIGreen)/pGreen['eff']/(pGreen['eci'] - gridCI) + 1

    # calculate FSCPs for grid
    renewablesShare_v, delta_cost_v = np.meshgrid(renewablesShare, delta_cost)
    pGreen['eci'] = renewablesShare_v * pGreen['eci'] + (1-renewablesShare_v) * gridCI
    CIBlue, CIGreen = __getCIs(pBlue, pGreen)
    fscp = delta_cost_v / (CIBlue - CIGreen)

    for x in range(len(renewablesShare)):
        for y in range(len(delta_cost)):
            if (CIBlue-CIGreen[x, y]) < 0:
                fscp[x, y] = zmax+10.0

    # add traces
    traces.append(go.Heatmap(x=renewablesShare * 100, y=delta_cost, z=fscp,
                             zsmooth='best', showscale=False, hoverinfo='skip',
                             zmin=zmin, zmax=zmax,
                             colorscale=colourscale,
                             colorbar=dict(
                                 x=1.0,
                                 y=0.5,
                                 len=1.0,
                                 title='FSCP',
                                 titleside='top',
                             )))

    traces.append(go.Contour(x=renewablesShare * 100, y=delta_cost, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=True,
                                 start=zmin,
                                 end=zmax,
                                 size=linedensity,
                             )))

    # determine other xaxis ranges
    pGreen = getCIParamsGreen(currentParams, fuelGreen, gwp)
    pGreenOther = getCIParamsGreen(currentParams, fuelGreen, gwpOther)
    # b_1 + eff*(p_1*eci_1 + (1-p_1)*gci_1) = b_2 + eff*(p_2*eci_2 + (1-p_2)*gci_2)
    # eff*p_2*(eci_2-gci_2) = b_1-b_2 + eff*(gci_1-gci_2) + eff*p_1*(eci_1-gci_1)
    # p_2 = (b_1-b_2 + eff*(gci_1-gci_2) + eff*p_1*(eci_1-gci_1))/(eff*(eci_2-gci_2))
    range2  = [(pGreen['b']-pGreenOther['b'] + pGreen['eff']*(gridCI-gridCIOther) + pGreen['eff']*x*(pGreen['eci']-gridCI))/
               (pGreenOther['eff'] * (pGreenOther['eci']-gridCIOther)) for x in [xmin, xmax]]
    range3 = [CIGreen[0][0], CIGreen[0][-1]]

    return traces, range2, range3, xvline


def __getXAxesStyle(calcedRanges: dict, config: dict):
    vspace = config['vertical_spacing']

    # settings for x axes 1 to 15 (6 and 11 are undefined)
    axisSetings = [
        (True, 1000, 'bottom', 'y', None, None, None),
        (True, 100, 'bottom', 'y2', None, None, 25.0),
        (True, 100, 'bottom', 'y3', None, None, 25.0),
        (True, 100, 'bottom', 'y4', None, None, 25.0),
        (True, 100, 'bottom', 'y5', None, None, 25.0),
        (False, None, None, None, None, None, None),
        (True, 100, 'bottom', 'free', 'x2', 0.5+vspace/2, None),
        (True, 100, 'bottom', 'free', 'x3', 0.5+vspace/2, None),
        (True, 100, 'bottom', 'free', 'x4', 0.0, None),
        (True, 100, 'bottom', 'free', 'x5', 0.0, None),
        (False, None, None, None, None, None, None),
        (True, 1000, 'top', 'free', 'x2', 1.0, None),
        (True, 1000, 'top', 'free', 'x3', 1.0, None),
        (True, 1000, 'top', 'free', 'x4', 0.5-vspace/2, 0.0),
        (True, 1000, 'top', 'free', 'x5', 0.5-vspace/2, 0.0),
    ]

    newAxes = {}
    for i, settings in enumerate(axisSetings):
        add, factor, side, anchor, overlay, position, standoff = settings

        if not add:
            continue

        axisName = f"xaxis{i + 1}"

        if axisName in calcedRanges:
            ran = [r * factor for r in calcedRanges[axisName]]
        else:
            ran = [config['plotting'][f"{axisName}_min"] * factor,
                   config['plotting'][f"{axisName}_max"] * factor]

        title = config['labels'][axisName]

        newAxes[axisName] = dict(title=title,
                                 range=ran,
                                 side=side,
                                 anchor=anchor,
                                 ticks='outside',
                                 )

        if overlay is not None:
            newAxes[axisName]['overlaying'] = overlay

        if position is not None:
            newAxes[axisName]['position'] = position

        if standoff is not None:
            newAxes[axisName]['title'] = dict(text=title, standoff=standoff)

    newAxes['xaxis7']['ticklen'] = 25.0
    newAxes['xaxis7']['tick0'] = 0.0
    newAxes['xaxis7']['dtick'] = 1.0

    newAxes['xaxis8']['ticklen'] = 25.0
    newAxes['xaxis8']['tick0'] = 0.0
    newAxes['xaxis8']['dtick'] = 1.0

    #newAxes['xaxis9']['ticklen'] = 25.0
    #newAxes['xaxis10']['ticklen'] = 25.0

    return newAxes


def __convertFuelData(fuelData: pd.DataFrame, fuel_x: str, fuel_y: str):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y").\
                   dropna()

    tmp['year'] = tmp['year_x']
    tmp['delta_cost'] = tmp['cost_y'] - tmp['cost_x']
    tmp['delta_ci'] = tmp['ci_x'] - tmp['ci_y']
    tmp['delta_cost_u'] = np.sqrt(tmp['cost_u_x']**2 + tmp['cost_u_y']**2)
    tmp['delta_ci_u'] = np.sqrt(tmp['ci_u_x']**2 + tmp['ci_u_y']**2)

    FSCPData = tmp[['fuel_x', 'delta_cost', 'delta_cost_u', 'delta_ci', 'delta_ci_u', 'year']]

    return FSCPData


def __getCIs(pBlue, pGreen):
    CIBlue = getCIBlue(**pBlue)
    CIGreen = getCIGreen(**pGreen)

    return sum(CIBlue[comp][0] for comp in CIBlue),\
           sum(CIGreen[comp][0] for comp in CIGreen)


def __getColourScale(config: dict):
    zmin = config['colourscale']['FSCPmin']
    zmax = config['colourscale']['FSCPmax']
    zran = config['colourscale']['FSCPmax'] - config['colourscale']['FSCPmin']
    csm = config['colourscale']['FSCPmid'] / zran

    colourscale = [
        [0.0, config['colours']['heatmap_low']],
        [csm, config['colours']['heatmap_medium']],
        [1.0, config['colours']['heatmap_high']],
    ]

    return zmin, zmax, colourscale
