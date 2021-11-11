import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb


def plotFig5(fullParams: pd.DataFrame, fuelData: pd.DataFrame,
             config: dict, scenario_name = "", export_img: bool = True):
    # produce figure
    fig = __produceFigure(fullParams, fuelData, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig5" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __produceFigure(fullParams: pd.DataFrame, fuelData: pd.DataFrame, config: dict):
    # plot
    fig = go.Figure()

    # get data
    fullParams = fullParams.query("year==2050")
    greenData = fuelData.query("year==2050 & fuel=='green RE'").reset_index(drop=True).iloc[0]

    CR = 'leb'
    GWP = 'gwp100'

    ci_blue_base = fullParams.query(f"name=='ci_blue_base_{CR}_{GWP}'").iloc[0].value
    ci_blue_methaneleakage = fullParams.query(f"name=='ci_blue_methaneleakage_{CR}_{GWP}'").iloc[0].value

    # add traces
    leakage = np.linspace(config['plotting']['leakage_min'], config['plotting']['leakage_max'], config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting']['cost_min'], config['plotting']['cost_max'], config['plotting']['n_samples'])
    leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
    fscp = delta_cost_v / (ci_blue_base + leakage_v * ci_blue_methaneleakage - greenData.ci)

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
