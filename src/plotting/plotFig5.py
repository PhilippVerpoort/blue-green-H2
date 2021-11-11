import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.data.calc_ci import getCIParamsBlue, getCIParamsGreen, getCIGreen, getCIBlue
from src.data.calc_fuels import getCurrentAsDict


def plotFig5(fullParams: pd.DataFrame, fuelData: pd.DataFrame, fuels: dict, gwp: str,
             config: dict, scenario_name = "", export_img: bool = True):
    # produce figure
    fig = __produceFigure(fullParams, fuelData, fuels, gwp, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig5" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __produceFigure(fullParams: pd.DataFrame, fuelData: pd.DataFrame, fuels: dict, gwp: str, config: dict):
    # plot
    fig = go.Figure()

    # define data for plot grid
    leakage = np.linspace(config['plotting']['leakage_min'], config['plotting']['leakage_max'], config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting']['cost_min'], config['plotting']['cost_max'], config['plotting']['n_samples'])

    # calculate CI data from params
    fuelBlue = fuels[config['fuelBlue']]
    fuelGreen = fuels[config['fuelGreen']]

    currentParams = getCurrentAsDict(fullParams, config['fuelYear'])
    pBlue = getCIParamsBlue(currentParams, fuelBlue, gwp)
    pGreen = getCIParamsGreen(currentParams, fuelGreen, gwp)

    # calculate FSCPs for grid
    leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
    pBlue['mlr'] = leakage_v
    fscp = delta_cost_v / __getCostDiff(pBlue, pGreen)

    # add traces
    fig.add_trace(go.Heatmap(x=leakage*100, y=delta_cost, z=fscp,
                             zsmooth='best', showscale=True, hoverinfo='skip',
                             colorscale=[
                                 [0.00, config['colours']['heatmap_low']],
                                 [0.50, config['colours']['heatmap_medium']],
                                 [1.00, config['colours']['heatmap_high']],
                             ],
                             colorbar=dict(
                                 x=1.0,
                                 y=0.5,
                                 len=1.0,
                                 title='FSCP',
                                 titleside='top',
                             )))

    fig.add_trace(go.Contour(x=leakage*100, y=delta_cost, z=fscp,
                             showscale=False, contours_coloring='lines', hoverinfo='skip',
                             colorscale=[
                                 [0.0, '#000000'],
                                 [1.0, '#000000'],
                             ],
                             contours=dict(
                                 showlabels=True,
                                 start=50,
                                 end=2000,
                                 size=50,
                             )))

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['ci'], range=[config['plotting']['leakage_min']*100, config['plotting']['leakage_max']*100],
                                 tickmode='linear', tick0=0.0, dtick=1.0),
                      yaxis=dict(title=config['labels']['cost'], range=[config['plotting']['cost_min'], config['plotting']['cost_max']]))

    return fig


def __getCostDiff(pBlue, pGreen):
    CIBlue = getCIBlue(**pBlue)
    CIGreen = getCIGreen(**pGreen)

    return sum(CIBlue[comp][0] for comp in CIBlue) - sum(CIGreen[comp][0] for comp in CIGreen)
