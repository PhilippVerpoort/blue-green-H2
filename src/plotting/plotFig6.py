import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.calc_cost import getCostParamsBlue, getCostParamsGreen, getCostBlue, getCostGreen
from src.data.calc_fuels import getCurrentAsDict


def plotFig6(fullParams: pd.DataFrame, fuels: dict,
             config: dict, export_img: bool = True):
    # produce figure
    fig = __produceFigure(fullParams, fuels, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig6.png")

    return fig


def __produceFigure(fullParams: pd.DataFrame, fuels: dict, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=5,
                        shared_yaxes=True,
                        horizontal_spacing=0.02)

    # get data
    fuelBlue = fuels[config['fuelBlue']]
    fuelGreen = fuels[config['fuelGreen']]

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getCostParamsBlue(*currentParams, fuelBlue)
    pGreen = getCostParamsGreen(*currentParams, fuelGreen)

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
        fig.add_trace(go.Scatter(x=x, y=delta, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=j)

    # add blue traces
    varyBlueParams = ['p_ng', 'C_pl']
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
        if par=='C_pl':
            x = x/10**6
        fig.add_trace(go.Scatter(x=x, y=delta, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=j)

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
