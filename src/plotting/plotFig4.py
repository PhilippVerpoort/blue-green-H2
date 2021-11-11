import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb


def plotFig4(fuelSpecs: dict, fuelData: pd.DataFrame, plotConfig: dict,
             scenario_name = "", export_img: bool = True):
    # combine fuel specs with plot config from YAML file
    config = {**fuelSpecs, **plotConfig}

    # produce figure
    fig = __produceFigure(fuelData, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig4" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __produceFigure(fuelData: pd.DataFrame, config: dict):
    # plot
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.05)

    # add FSCP traces
    traces = __addFSCPContours(fuelData, config)
    for col, trace in traces:
        fig.add_trace(trace, row=1, col=col)

    # add scatter curves
    traces = __addFSCPScatterCurves(fuelData, config)
    for trace in traces:
        for j in range(2):
            if j: trace.showlegend = False
            fig.add_trace(trace, row=1, col=j+1)

    # add rectangle
    for j in range(2):
        fig.add_shape(x0=config['plotting']['ci_min2']*1000,
                      x1=config['plotting']['ci_max2']*1000,
                      y0=config['plotting']['cost_min2'],
                      y1=config['plotting']['cost_max2'],
                      line=dict(
                          color=config['rectcolour'],
                          width=2,
                      ),
                      row=1, col=j+1)

    # set plotting ranges
    fig.update_layout(xaxis =dict(title=config['labels']['ci'], range=[config['plotting']['ci_min1']*1000, config['plotting']['ci_max1']*1000]),
                      xaxis2=dict(title=config['labels']['ci'], range=[config['plotting']['ci_min2']*1000, config['plotting']['ci_max2']*1000]),
                      yaxis =dict(title=config['labels']['cost'], range=[config['plotting']['cost_min1'], config['plotting']['cost_max1']]),
                      yaxis2=dict(title="", range=[config['plotting']['cost_min2'], config['plotting']['cost_max2']]))

    # legend settings
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="center",
            x=0.34,
            bgcolor = 'rgba(255,255,255,0.6)',
            font = dict(size = 12),
        ),
    )

    return fig


def __addFSCPScatterCurves(fuelData: pd.DataFrame, config: dict):
    traces = []

    for fuel_x in ['blue LEB', 'blue HEB']:
        fuel_y = 'green RE'
        thisData = __convertFuelData(fuelData, fuel_x, fuel_y)

        name = f"FSCP {config['names'][fuel_x]} to {config['names'][fuel_y]}"

        traces.append(go.Scatter(x=thisData.delta_ci*1000, y=thisData.delta_cost,
            error_x=dict(type='data', array=thisData.delta_ci_u*1000),
            error_y=dict(type='data', array=thisData.delta_cost_u),
            name=name,
            line=dict(color=config['fscp_colours'][f"{fuel_x} to {fuel_y}"]),
            mode='lines+markers',
            customdata=thisData.year,
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity difference: %{{x:.2f}}±%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference: %{{y:.2f}}±%{{error_y.array:.2f}}<extra></extra>",
        ))

    return traces


def __addFSCPContours(fuelData: pd.DataFrame, config: dict):
    traces = []

    for col in range(2):
        delta_ci = np.linspace(config['plotting'][f"ci_min{col+1}"], config['plotting'][f"ci_max{col+1}"], config['plotting']['n_samples'])
        delta_cost = np.linspace(config['plotting'][f"cost_min{col+1}"], config['plotting'][f"cost_max{col+1}"], config['plotting']['n_samples'])
        delta_ci_v, delta_cost_v = np.meshgrid(delta_ci, delta_cost)
        fscp = delta_cost_v / delta_ci_v

        zmin=config['colourscale']['FSCPmin']
        zmax=config['colourscale']['FSCPmax']
        zran=config['colourscale']['FSCPmax']-config['colourscale']['FSCPmin']
        csm=config['colourscale']['FSCPmid']/zran

        colorscale = [
            [0.0, config['colours']['heatmap_low']],
            [csm, config['colours']['heatmap_medium']],
            [1.0, config['colours']['heatmap_high']],
        ]

        traces.append((col+1, go.Heatmap(x=delta_ci * 1000, y=delta_cost, z=fscp,
                                         zsmooth='best', showscale=True, hoverinfo='skip',
                                         zmin=zmin, zmax=zmax,
                                         colorscale=colorscale,
                                         colorbar=dict(
                                             x=1.0,
                                             y=0.4,
                                             len=0.8,
                                             title='FSCP',
                                             titleside='top',
                                         ))))

        traces.append((col+1, go.Contour(x=delta_ci * 1000, y=delta_cost, z=fscp,
                                         showscale=False, contours_coloring='lines', hoverinfo='skip',
                                         colorscale=[
                                             [0.0, '#000000'],
                                             [1.0, '#000000'],
                                         ],
                                         contours=dict(
                                             showlabels=True,
                                             labelformat='.4',
                                             start=-2000,
                                             end=10000,
                                             size=config['linedensity'][f"plot{col+1}"],
                                         ))))

    return traces


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
