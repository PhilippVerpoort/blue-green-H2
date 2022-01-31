from string import ascii_lowercase

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.fuels.calc_ghgi import getGHGIParamsBlue, getGHGIParamsGreen, getGHGIGreen, getGHGIBlue
from src.data.fuels.calc_fuels import getCurrentAsDict
from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig5(fuelSpecs: dict, fuelData: pd.DataFrame, fullParams: pd.DataFrame, fuels: dict,
             plotConfig: dict, export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # produce figure
    fig = __produceFigure(fuelData, fullParams, fuels, config)

    # write figure to image file
    if export_img:
        w_mm = 180.0
        h_mm = 81.0

        fs_sm = getFontSize(5.0)
        fs_lg = getFontSize(7.0)

        fig.update_layout(font_size=fs_sm)
        fig.update_annotations(font_size=fs_sm)
        for annotation in fig['layout']['annotations'][:5]:
            annotation['font']['size'] = fs_lg
        fig.update_xaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)
        fig.update_yaxes(title_font_size=fs_sm,
                         tickfont_size=fs_sm)

        fig.write_image("output/fig5.png", **getImageSize(w_mm, h_mm))

    return fig


def __produceFigure(fuelData: pd.DataFrame, fullParams: pd.DataFrame, fuels: dict, config: dict):
    # plot
    fig = make_subplots(rows=2,
                        cols=4,
                        specs=[
                            [{"rowspan": 2, "colspan": 2}, None, {}, {}],
                            [None, None, {}, {}],
                        ],
                        subplot_titles=ascii_lowercase,
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
    annotationStyling = dict(xanchor='left', yanchor='bottom', showarrow=False, bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')
    fuelGreen = fuels[config['fuelGreen']]

    fuelBlue = fuels[config['fuelBlueLeft']]
    xmin, xmax = config['plotting']['xaxis2_min'], config['plotting']['xaxis2_max']
    traces, calcedRanges['xaxis7'], calcedRanges['xaxis12'] = __addFSCPSubplotContoursTop(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot2"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[1])
    fig.add_annotation(x=0.1, y=-9.0, xref="x2", yref="y2", text=fuelBlue['desc'], **annotationStyling)

    fuelBlue = fuels[config['fuelBlueRight']]
    xmin, xmax = config['plotting']['xaxis3_min'], config['plotting']['xaxis3_max']
    traces, calcedRanges['xaxis8'], calcedRanges['xaxis13'] = __addFSCPSubplotContoursTop(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot3"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[2])
    fig.add_annotation(x=0.1, y=-9.0, xref="x3", yref="y3", text=fuelBlue['desc'], **annotationStyling)

    fuelBlue = fuels[config['fuelBlueLeft']]
    xmin, xmax = config['plotting']['xaxis4_min'], config['plotting']['xaxis4_max']
    traces, calcedRanges['xaxis9'], calcedRanges['xaxis14'], xvline = __addFSCPSubplotContoursBottom(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot4"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[3])
    #fig.add_vline(x=xvline*100, line_width=3, line_color="black", **rowcol_mapping[3])
    fig.add_annotation(x=80.4, y=-9.0, xref="x4", yref="y4", text=fuelBlue['desc'], **annotationStyling)

    fuelBlue = fuels[config['fuelBlueRight']]
    xmin, xmax = config['plotting']['xaxis5_min'], config['plotting']['xaxis5_max']
    traces, calcedRanges['xaxis10'], calcedRanges['xaxis15'], xvline = __addFSCPSubplotContoursBottom(fullParams, fuelGreen, fuelBlue, xmin, xmax, config, zmin, zmax, colourscale, config['linedensity'][f"plot5"])
    for trace in traces:
        fig.add_trace(trace, **rowcol_mapping[4])
    #fig.add_vline(x=xvline*100, line_width=5, line_color="black", **rowcol_mapping[4])
    fig.add_annotation(x=80.4, y=-9.0, xref="x5", yref="y5", text=fuelBlue['desc'], **annotationStyling)


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

    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.005,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )


    # update axis styling
    for axis in ['xaxis', 'xaxis2', 'xaxis3', 'xaxis4', 'xaxis5', 'yaxis', 'yaxis2', 'yaxis3', 'yaxis4', 'yaxis5']:
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
    fig.update_xaxes(ticks='outside')


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


    return fig


def __addFSCPContours(config: dict, zmin: float, zmax: float, colourscale: list):
    traces = []

    delta_ghgi = np.linspace(config['plotting'][f"xaxis1_min"], config['plotting'][f"xaxis1_max"], config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting'][f"yaxis1_min"], config['plotting'][f"yaxis1_max"], config['plotting']['n_samples'])
    delta_ghgi_v, delta_cost_v = np.meshgrid(delta_ghgi, delta_cost)
    fscp = delta_cost_v / delta_ghgi_v

    traces.append(go.Heatmap(x=delta_ghgi * 1000, y=delta_cost, z=fscp,
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

    traces.append(go.Contour(x=delta_ghgi * 1000, y=delta_cost, z=fscp,
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

    for fuel_x in [config['fuelBlueRight']]:
        fuel_y = config['fuelGreen']
        thisData = __convertFuelData(fuelData, fuel_x, fuel_y)

        name = f"Comparing {config['names'][fuel_x]} with {config['names'][fuel_y]}"
        col = config['fscp_colours'][f"{fuel_x} to {fuel_y}"]

        traces.append(go.Scatter(x=thisData.delta_ghgi * 1000, y=thisData.delta_cost,
            text=thisData.year,
            textposition="top right",
            textfont=dict(color=col),
            name=name,
            legendgroup=f"{fuel_x}__{fuel_y}",
            line=dict(color=col),
            marker_size=10,
            mode='lines+markers+text',
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity difference: %{{x:.2f}}±%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference (w/o CP): %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>",
        ))

        thisData = thisData.query(f"year==[2025,2030,2040,2050]")

        traces.append(go.Scatter(x=thisData.delta_ghgi * 1000, y=thisData.delta_cost,
            error_x=dict(type='data', array=thisData.delta_ghgi_uu*1000, arrayminus=thisData.delta_ghgi_ul*1000, thickness=2),
            error_y=dict(type='data', array=thisData.delta_cost_uu, arrayminus=thisData.delta_cost_ul, thickness=2),
            line=dict(color=col),
            marker_size=0.000001,
            showlegend=False,
            mode='markers',
        ))

    return traces


def __addFSCPSubplotContoursTop(fullParams: pd.DataFrame, fuelGreen: dict, fuelBlue: dict, xmin: float, xmax: float, config: dict, zmin: float, zmax: float, colourscale: list, linedensity: float):
    traces = []


    # define data for plot grid
    leakage = np.linspace(xmin, xmax, config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting']['yaxis1_min'], config['plotting']['yaxis1_max'], config['plotting']['n_samples'])

    # calculate GHGI data from params
    gwp = 'gwp100'
    gwpOther = 'gwp20' if gwp == 'gwp100' else 'gwp100'

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getGHGIParamsBlue(*currentParams, fuelBlue, gwp)
    pGreen = getGHGIParamsGreen(*currentParams, fuelGreen, gwp)

    # calculate FSCPs for grid
    leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
    pBlue['mlr'] = (leakage_v, 0, 0)
    GHGIBlue, GHGIGreen = __getGHGIs(pBlue, pGreen)
    fscp = delta_cost_v / (GHGIBlue - GHGIGreen)

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
    pBlue = getGHGIParamsBlue(*currentParams, fuelBlue, gwp)
    pBlueOther = getGHGIParamsBlue(*currentParams, fuelBlue, gwpOther)
    # ghgi0_1 + p_1 * ghgim_1 = ghgi0_2 + p_2 * ghgim_2
    # p_2 = (p_1*ghgim_1+ghgi0_1-ghgi0_2)/ghgim_2
    range2  = [(x*pBlue['mghgi']+pBlue['b'][0]-pBlueOther['b'][0]) / pBlueOther['mghgi']
               for x in [xmin, xmax]]
    range3 = [GHGIBlue[0][0], GHGIBlue[0][-1]]

    return traces, range2, range3


def __addFSCPSubplotContoursBottom(fullParams: pd.DataFrame, fuelGreen: dict, fuelBlue: dict, xmin: float, xmax: float,
                                   config: dict, zmin: float, zmax: float, colourscale: list, linedensity: float):
    traces = []

    # turn this on to set methane leakage to zero in subplots (d) and (e)
    #fullParams = fullParams.copy()
    #fullParams.loc[fullParams['name'] == 'ghgi_ng_methaneleakage', 'value'] = 0.0

    # define data for plot grid
    renewablesShare = np.linspace(xmin, xmax, config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting'][f"yaxis1_min"], config['plotting'][f"yaxis1_max"], config['plotting']['n_samples'])

    # calculate GHGI data from params
    gwp = 'gwp100'
    gwpOther = 'gwp20' if gwp == 'gwp100' else 'gwp100'

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getGHGIParamsBlue(*currentParams, fuelBlue, gwp)
    pGreen = getGHGIParamsGreen(*currentParams, fuelGreen, gwp)

    # carbon intensity of grid electricity (needs to be obtained from data file in future after green GHGI has been tidied up)
    gridGHGI = 0.397
    gridGHGIOther = 0.434

    # calculate xvline
    # 0 = GHGIGreen(x) - GHGIBlue =  GHGIGreen(1) + eff* ((x-1) * eghgi + (1-x) * gghgi) - GHGIBlue
    # ((GHGIBlue - GHGIGreen)/eff + eghgi - gghgi) / (eghgi - gghgi) = x
    GHGIBlue, GHGIGreen = __getGHGIs(pBlue, pGreen)
    xvline = (GHGIBlue - GHGIGreen)/pGreen['eff']/(pGreen['eghgi'][0] - gridGHGI) + 1

    # calculate FSCPs for grid
    renewablesShare_v, delta_cost_v = np.meshgrid(renewablesShare, delta_cost)
    pGreen['eghgi'] = (renewablesShare_v * pGreen['eghgi'][0] + (1-renewablesShare_v) * gridGHGI, 0, 0)
    GHGIBlue, GHGIGreen = __getGHGIs(pBlue, pGreen)
    fscp = delta_cost_v / (GHGIBlue - GHGIGreen)

    for x in range(len(renewablesShare)):
        for y in range(len(delta_cost)):
            if (GHGIBlue-GHGIGreen[x, y]) < 0:
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
    pGreen = getGHGIParamsGreen(*currentParams, fuelGreen, gwp)
    pGreenOther = getGHGIParamsGreen(*currentParams, fuelGreen, gwpOther)
    # b_1 + eff*(p_1*eghgi_1 + (1-p_1)*gghgi_1) = b_2 + eff*(p_2*eghgi_2 + (1-p_2)*gghgi_2)
    # eff*p_2*(eghgi_2-gghgi_2) = b_1-b_2 + eff*(gghgi_1-gghgi_2) + eff*p_1*(eghgi_1-gghgi_1)
    # p_2 = (b_1-b_2 + eff*(gghgi_1-gghgi_2) + eff*p_1*(eghgi_1-gghgi_1))/(eff*(eghgi_2-gghgi_2))
    range2  = [(pGreen['b'][0]-pGreenOther['b'][0] + pGreen['eff']*(gridGHGI-gridGHGIOther) + pGreen['eff']*x*(pGreen['eghgi'][0]-gridGHGI))/
               (pGreenOther['eff'] * (pGreenOther['eghgi'][0]-gridGHGIOther)) for x in [xmin, xmax]]
    range3 = [GHGIGreen[0][0], GHGIGreen[0][-1]]

    return traces, range2, range3, xvline


def __getXAxesStyle(calcedRanges: dict, config: dict):
    vspace = config['vertical_spacing']

    # settings for x axes 1 to 15 (6 and 11 are undefined)
    axisSetings = [
        (True, 1000, 'bottom', 'y', None, None, None),
        (True, 100, 'bottom', 'y2', None, None, 25.0),
        (True, 100, 'bottom', 'y3', None, None, 25.0),
        (True, 100, 'bottom', 'y4', None, None, None),
        (True, 100, 'bottom', 'y5', None, None, None),
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

        newAxes[axisName] = dict(
            title=title,
            range=ran,
            side=side,
            anchor=anchor,
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

    newAxes['xaxis9']['ticklen'] = 25.0
    newAxes['xaxis10']['ticklen'] = 25.0

    return newAxes


def __convertFuelData(fuelData: pd.DataFrame, fuel_x: str, fuel_y: str):
    fuelData = fuelData[['fuel', 'type', 'year', 'cost', 'cost_uu', 'cost_ul', 'ghgi', 'ghgi_uu', 'ghgi_ul']]

    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y").\
                   dropna()

    tmp['year'] = tmp['year_x']

    tmp['delta_cost'] = tmp['cost_y'] - tmp['cost_x']
    tmp['delta_cost_uu'] = tmp['cost_uu_y'] + tmp['cost_ul_x']
    tmp['delta_cost_ul'] = tmp['cost_ul_y'] + tmp['cost_uu_x']

    tmp['delta_ghgi'] = tmp['ghgi_x'] - tmp['ghgi_y']
    tmp['delta_ghgi_uu'] = tmp['ghgi_uu_x'] + tmp['ghgi_ul_y']
    tmp['delta_ghgi_ul'] = tmp['ghgi_ul_x'] + tmp['ghgi_uu_y']

    FSCPData = tmp[['fuel_x', 'delta_cost', 'delta_cost_uu', 'delta_cost_ul',
                    'delta_ghgi', 'delta_ghgi_uu', 'delta_ghgi_ul', 'year']]

    return FSCPData


def __getGHGIs(pBlue, pGreen):
    GHGIBlue = getGHGIBlue(**pBlue)
    GHGIGreen = getGHGIGreen(**pGreen)

    return sum(GHGIBlue[comp][0] for comp in GHGIBlue),\
           sum(GHGIGreen[comp][0] for comp in GHGIGreen)


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
