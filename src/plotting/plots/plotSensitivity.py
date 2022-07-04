import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.fuels.calc_cost import getCostParamsBlue, getCostParamsGreen, getCostBlue, getCostGreen
from src.timeit import timeit


@timeit
def plotSensitivity(fuels: dict, config: dict):
    # produce figure
    fig = __produceFigure(fuels, config)

    # styling figure
    __styling(fig)

    return {'fig6': fig}


def __produceFigure(fuels: dict, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=5,
                        shared_yaxes=True,
                        horizontal_spacing=0.02)

    # get data
    techBlue = fuels[config['fuelBlue'].split('-')[0]]['tech_type']

    pBlue = getCostParamsBlue(config['params'][config['fuelBlue']].query(f"year=={config['fuelYear']}").droplevel(level=1), techBlue)
    pGreen = getCostParamsGreen(config['params'][config['fuelBlue']].query(f"year=={config['fuelYear']}").droplevel(level=1))

    # add green traces
    varyGreenParams = ['p_el', 'c_pl', 'ocf']
    for i, par in enumerate(varyGreenParams):
        j = i + 1
        pGreenMod = pGreen.copy()
        hasUncertainty = isinstance(pGreenMod[par], tuple)
        if hasUncertainty:
            pGreenMod[par] = pGreenMod[par][0]
        pGreenMod[par] = np.linspace(pGreenMod[par] - config['plotting'][f"delta_x{j}"],
                                     pGreenMod[par] + config['plotting'][f"delta_x{j}"],
                                     config['plotting']['n_samples'])
        x = pGreenMod[par]
        if hasUncertainty:
            pGreenMod[par] = (pGreenMod[par], 0.0, 0.0)
        delta, delta_u = __getCostDiff(pBlue, pGreenMod)
        if par=='c_pl':
            x = x/10**3
        elif par=='ocf':
            x = x*100
        fig.add_trace(
            go.Scatter(x=x, y=delta, hoverinfo='skip', mode='lines', showlegend=False, line_width=3.0,),
            row=1, col=j
        )

    # add blue traces
    varyBlueParams = ['p_ng', 'c_pl']
    for i, par in enumerate(varyBlueParams):
        j = i + 1 + len(varyGreenParams)
        pBlueMod = pBlue.copy()
        hasUncertainty = isinstance(pBlueMod[par], tuple)
        if hasUncertainty:
            pBlueMod[par] = pBlueMod[par][0]
        pBlueMod[par] = np.linspace(pBlueMod[par] - config['plotting'][f"delta_x{j}"],
                                    pBlueMod[par] + config['plotting'][f"delta_x{j}"],
                                    config['plotting']['n_samples'])
        x = pBlueMod[par]
        if hasUncertainty:
            pBlueMod[par] = (pBlueMod[par], 0.0, 0.0)
        delta, delta_u = __getCostDiff(pBlueMod, pGreen)
        if par=='c_pl':
            x = x/10**3
        fig.add_trace(
            go.Scatter(x=x, y=delta, hoverinfo='skip', mode='lines', showlegend=False, line_width=3.0,),
            row=1, col=j,
        )

    # add horizontal line
    delta, _ = __getCostDiff(pBlue, pGreen)
    fig.add_hline(y=delta)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['x1']),
                      xaxis2=dict(title=config['labels']['x2']),
                      xaxis3=dict(title=config['labels']['x3']),
                      xaxis4=dict(title=config['labels']['x4']),
                      xaxis5=dict(title=config['labels']['x5']),
                      yaxis=dict(title=config['labels']['cost'],
                                 range=[delta-config['plotting']['delta_cost'],
                                        delta+config['plotting']['delta_cost']]))

    return fig


def __getCostDiff(pBlue, pGreen):
    costBlue = getCostBlue(**pBlue)
    costGreen = getCostGreen(**pGreen)

    delta = sum(costGreen[comp][0] for comp in costGreen) - sum(costBlue[comp][0] for comp in costBlue)
    delta_u = np.sqrt(sum(costGreen[comp][1]**2 for comp in costGreen) + sum(costBlue[comp][1]**2 for comp in costBlue))

    return delta, delta_u


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
