import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.fuels.calc_cost import getCostParamsBlue, getCostParamsGreen, getCostBlue, getCostGreen, paramsCost, \
    evalCost
from src.data.fuels.calc_ghgi import getGHGIBlue, getGHGIGreen, paramsGHGI, evalGHGI
from src.timeit import timeit


@timeit
def plotSensitivityFSCP(fuels: dict, config: dict):
    # produce figure
    fig = __produceFigure(fuels, config)

    # styling figure
    __styling(fig)

    return {'fig9': fig}


def __produceFigure(fuels: dict, config: dict):
    # plot
    fig = make_subplots(
        rows=1,
        cols=len(config['sensitivity_params']),
        shared_yaxes=True,
        horizontal_spacing=0.02
    )


    # loop over fuels
    has_vline = []
    hasLegend = []
    for fid, fuelA, fuelB, year in [(fid, *f.split(' to '), y) for fid, f in enumerate(config['fuels']) for y in config['years']]:
        pAC, pAG = __getFuelPs(fuelA, fuels, config['params'][fuelA], year)
        pBC, pBG = __getFuelPs(fuelB, fuels, config['params'][fuelB], year)

        for j, item in enumerate(config['sensitivity_params'].items()):
            var, settings = item

            # get linspaces for parameters, x, and y
            x, ps, val = __calcLinspace(var, settings, config['n_samples'], pAC, pAG, pBC, pBG)
            fscp = __getFSCP(*ps, fuels[fuelA.split('-')[0]], fuels[fuelB.split('-')[0]])


            # cut off line going from infinity to minus infinity
            cutoff = 2000.0
            if j == 1 and fscp.max() > cutoff:
                fscp[:fscp.argmax()] = cutoff


            # draw lines
            fig.add_trace(
                go.Scatter(
                    x=x*settings['scale'],
                    y=fscp,
                    hoverinfo='skip',
                    mode='lines',
                    showlegend=False,
                    line=dict(width=config['global']['lw_thin'], color=config['colour'], dash='dash' if fid else None),
                ),
                row=1, col=j+1,
            )


            # markers and vertical lines at x=0 for mode relative
            if settings['mode'] == 'relative':
                val = 0.0


            # add markers
            fscp = __getFSCP(pAC, pAG, pBC, pBG, fuels[fuelA.split('-')[0]], fuels[fuelB.split('-')[0]])
            fig.add_trace(
                go.Scatter(
                    x=[val*settings['scale']],
                    y=[fscp],
                    text=[year],
                    hoverinfo='skip',
                    mode='markers+text',
                    showlegend=False,
                    line=dict(width=config['global']['lw_default'], color=config['colour'], dash='dash' if fid else None),
                    marker=dict(symbol='circle-open', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': config['colour']},),
                    textposition=settings['textpos'][fid],
                    textfont=dict(color=config['colour']),
                ),
                row=1, col=j+1,
            )

            if fid not in hasLegend:
                hasLegend.append(fid)


            # add vertical lines
            vlineid = f"{var}-{year}" if settings['vline'] == 'peryear' else f"{var}"
            if vlineid not in has_vline:
                fig.add_vline(
                    x=val*settings['scale'],
                    line=dict(color='black', dash='dash'),
                    row=1,
                    col=j+1
                )

                fig.add_annotation(go.layout.Annotation(
                    text=f"Default {year}" if settings['vline'] == 'peryear' else 'Default',
                    x=val*settings['scale'],
                    xanchor='left',
                    y=config['yrange'][1],
                    yanchor='top',
                    showarrow=False,
                    textangle=90,
                ), row=1, col=j+1)

                has_vline.append(vlineid)


    # set x axes ranges and labels
    for j, item in enumerate(config['sensitivity_params'].items()):
        var, settings = item

        xrange = [settings['range'][0] * settings['scale'], settings['range'][1] * settings['scale']]

        if var == 'sh':
            xrange[-1] = 100.35

        axis = {
            'title': settings['label'],
            'range': xrange,
        }
        fig.update_layout(**{f"xaxis{j + 1 if j else ''}": axis})

        # add horizontal line for fscp=0
        fig.add_hline(0.0, row=1, col=j+1)


    # set y axis range and label
    fig.update_layout(yaxis=dict(
        title=config['ylabel'],
        range=config['yrange'],
    ))

    return fig


def __getFuelPs(fuel: str, fuels: dict, params: pd.DataFrame, year: int):
    fuelBasic = fuel.split('-')[0]
    pars = params.query(f"year=={year}").droplevel(level=1)

    gwp = 'gwp100'

    pC = paramsCost(pars, fuels[fuelBasic])
    pG = paramsGHGI(pars, fuels[fuelBasic], gwp)

    return pC, pG


def __calcLinspace(var, settings, n, *ps):
    ps = list(ps)

    x = np.linspace(*settings['range'], n)

    for k in [i for i in range(4) if var in ps[i]]:
        val = ps[k][var]
        hasUncertainty = isinstance(val, tuple)

        if hasUncertainty:
            val = val[0]

        ps[k] = ps[k].copy()

        if settings['mode'] == 'absolute':
            xplot = x
        elif settings['mode'] == 'relative':
            xplot = np.linspace(val + settings['range'][0], val + settings['range'][1], n)
        else:
            raise Exception(f"Unknown mode selected for variable {var}: {settings['mode']}")

        ps[k][var] = (xplot, 0.0, 0.0) if hasUncertainty else xplot

    return x, ps, val


def __getFSCP(pAC, pAG, pBC, pBG, fuelA, fuelB):
    costA = evalCost(pAC, fuelA)
    costB = evalCost(pBC, fuelB)
    ghgiA = evalGHGI(pAG, fuelA)
    ghgiB = evalGHGI(pBG, fuelB)

    cost_diff = sum(costB[comp][0] for comp in costB) - sum(costA[comp][0] for comp in costA)
    ghgi_diff = sum(ghgiA[comp][0] for comp in ghgiA) - sum(ghgiB[comp][0] for comp in ghgiB)

    if isinstance(cost_diff, np.ndarray):
        fscp = np.maximum(cost_diff, [0.0]*len(cost_diff)) / ghgi_diff
    else:
        fscp = max(cost_diff, 0.0) / ghgi_diff

    return fscp


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=1.00,
            xanchor='left',
            x=1.02,
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


    # update figure background colour and font colour and type
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 1.0)',
        plot_bgcolor='rgba(255, 255, 255, 0.0)',
        font_color='black',
        font_family='Helvetica',
    )
