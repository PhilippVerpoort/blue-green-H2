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
        horizontal_spacing=0.04
    )


    # loop over fuels
    for fuelA, fuelB, year in [(*f.split(' to '), y) for f in config['fuels'] for y in config['years']]:
        pAC, pAG = __getFuelPs(fuelA, fuels, config['params'][fuelA], year)
        pBC, pBG = __getFuelPs(fuelB, fuels, config['params'][fuelB], year)

        for j, item in enumerate(config['sensitivity_params'].items()):
            var, settings = item
            ps = __calcLinspace(var, settings, config['n_samples'], pAC, pAG, pBC, pBG)
            x = np.linspace(0.0, settings['delta'], config['n_samples'])

            fscp = __getFSCP(*ps, fuels[fuelA.split('-')[0]], fuels[fuelB.split('-')[0]])


            # cut off line going from infinity to minus infinity
            cutoff = 2000.0
            if fscp.max() > cutoff:
                fscp[fscp.argmax():] = cutoff

            fig.add_trace(
                go.Scatter(
                    x=x*settings['scale'],
                    y=fscp,
                    hoverinfo='skip',
                    mode='lines',
                    showlegend=False,
                    line=dict(width=config['global']['lw_thin'], color=config['colour']),
                ),
                row=1, col=j+1,
            )

            fscp = __getFSCP(pAC, pAG, pBC, pBG, fuels[fuelA.split('-')[0]], fuels[fuelB.split('-')[0]])
            fig.add_hline(y=fscp, row=1, col=j+1)

            axis = {
                'title': settings['label'],
                'range': [x[0]*settings['scale'], x[-1]*settings['scale']],
            }
            fig.update_layout(**{f"xaxis{j+1 if j else ''}": axis})


    # set y plotting range
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

    for k in [i for i in range(4) if var in ps[i]]:
        val = ps[k][var]
        hasUncertainty = isinstance(val, tuple)

        if hasUncertainty:
            val = val[0]

        x = np.linspace(val, val + settings['delta'], n)

        ps[k] = ps[k].copy()
        ps[k][var] = (x, 0.0, 0.0) if hasUncertainty else x

    return ps


def __getFSCP(pAC, pAG, pBC, pBG, fuelA, fuelB):
    costA = evalCost(pAC, fuelA)
    costB = evalCost(pBC, fuelB)
    ghgiA = evalGHGI(pAG, fuelA)
    ghgiB = evalGHGI(pBG, fuelB)

    fscp = (sum(costB[comp][0] for comp in costB) - sum(costA[comp][0] for comp in costA)) / \
           (sum(ghgiA[comp][0] for comp in ghgiA) - sum(ghgiB[comp][0] for comp in ghgiB))

    return fscp


def __styling(fig: go.Figure):
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
