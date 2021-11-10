import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb


def plotFig4(fuelData: pd.DataFrame, scenario_name = "", export_img: bool = True):
    # load config setting from YAML file
    config = __getPlottingConfig()

    # produce figure
    fig = __produceFigure(fuelData, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig4" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __getPlottingConfig():
    configThis = yaml.load(open('input/plotting/config_fig4.yml', 'r').read(), Loader=yaml.FullLoader)
    return configThis


def __produceFigure(fuelData: pd.DataFrame, config: dict):
    # plot
    fig = go.Figure()

    # add traces
    delta_ci = np.linspace(config['plotting']['ci_min'], config['plotting']['ci_max'], config['plotting']['n_samples'])
    delta_cost = np.linspace(config['plotting']['cost_min'], config['plotting']['cost_max'], config['plotting']['n_samples'])
    delta_ci_v, delta_cost_v = np.meshgrid(delta_ci, delta_cost)
    fscp = delta_cost_v / delta_ci_v

    fig.add_trace(go.Heatmap(x=delta_ci*1000, y=delta_cost, z=fscp,
                             zsmooth='best', showscale=True, hoverinfo='skip',
                             colorscale=[
                                 [0.0, config['colours']['heatmap_low']],
                                 [0.1, config['colours']['heatmap_medium']],
                                 [1.0, config['colours']['heatmap_high']],
                             ],
                             colorbar=dict(
                                 x=1.0,
                                 y=0.5,
                                 len=1.0,
                                 title='FSCP',
                                 titleside='top',
                             )))

    fig.add_trace(go.Contour(x=delta_ci*1000, y=delta_cost, z=fscp,
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

    thisData = __calcFSCP(fuelData)

    fig.add_trace(go.Scatter(x=thisData.delta_ci*1000, y=thisData.delta_cost,
        line=dict(color='black'),
        mode='lines+markers',
    ))

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['ci'], range=[config['plotting']['ci_min']*1000, config['plotting']['ci_max']*1000]),
                      yaxis=dict(title=config['labels']['cost'], range=[config['plotting']['cost_min'], config['plotting']['cost_max']]))

    return fig

def __calcFSCP(fuelData):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   query("fuel_x=='blue LEB' & fuel_y=='green RE' & year_x==year_y").\
                   dropna()

    tmp['delta_cost'] = tmp['cost_y'] - tmp['cost_x']
    tmp['delta_ci'] = tmp['ci_x'] - tmp['ci_y']

    FSCPData = tmp[['delta_cost', 'delta_ci']]

    return FSCPData
