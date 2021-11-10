import numpy as np
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb


def plotFig6(fullParams: pd.DataFrame, fuelData: pd.DataFrame, scenario_name = "", export_img: bool = True):
    # load config setting from YAML file
    config = __getPlottingConfig()

    # produce figure
    fig = __produceFigure(fullParams, fuelData, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig6" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __getPlottingConfig():
    configThis = yaml.load(open('input/plotting/config_fig6.yml', 'r').read(), Loader=yaml.FullLoader)
    return configThis


def __produceFigure(fullParams: pd.DataFrame, fuelData: pd.DataFrame, config: dict):
    # plot
    fig = make_subplots(rows=1,
                        cols=5,
                        shared_yaxes=True,
                        horizontal_spacing=0.05)

    # get data
    fullParams = fullParams.query("year==2030")
    greenData = fuelData.query("year==2030 & fuel=='green RE'").reset_index(drop=True).iloc[0]
    blueData = fuelData.query("year==2030 & fuel=='blue LEB'").reset_index(drop=True).iloc[0]

    ES = 'wind'
    CR = 'leb'

    C_pl = fullParams.query(f"name=='cost_blue_capex_{CR}'").iloc[0].value
    P_pl = fullParams.query("name=='cost_blue_plantsize'").iloc[0].value
    p_ng = fullParams.query("name=='cost_ng_price'").iloc[0].value
    effb = fullParams.query(f"name=='cost_blue_eff_{CR}'").iloc[0].value
    c_CTS = fullParams.query("name=='cost_blue_cts'").iloc[0].value
    flh = fullParams.query("name=='cost_blue_flh'").iloc[0].value
    emi = fullParams.query(f"name=='cost_blue_emiForCTS_{CR}'").iloc[0].value

    c_pl = fullParams.query("name=='cost_green_capex'").iloc[0].value
    p_el = fullParams.query(f"name=='cost_green_elec_{ES}'").iloc[0].value
    eff = fullParams.query("name=='ci_green_eff'").iloc[0].value
    ocf = fullParams.query("name=='green_ocf'").iloc[0].value

    i = fullParams.query("name=='irate'").iloc[0].value
    n = fullParams.query("name=='lifetime'").iloc[0].value
    FCR = i*(1+i)**n/((1+i)**n-1)

    # add trace 1
    p_el_r = np.linspace(config['plotting']['x1_min'], config['plotting']['x1_max'], config['plotting']['n_samples'])
    delta_cost = FCR * c_pl/(ocf*8760) + p_el_r*eff - blueData.cost

    fig.add_trace(go.Scatter(x=p_el_r, y=delta_cost, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=1)

    # add trace 2
    c_pl_r = np.linspace(config['plotting']['x2_min'], config['plotting']['x2_max'], config['plotting']['n_samples'])
    delta_cost = FCR * c_pl_r/(ocf*8760) + p_el*eff - blueData.cost

    fig.add_trace(go.Scatter(x=c_pl_r/1000, y=delta_cost, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=2)

    # add trace 3
    ocf_r = np.linspace(config['plotting']['x3_min'], config['plotting']['x3_max'], config['plotting']['n_samples'])
    delta_cost = FCR * c_pl/(ocf_r*8760) + p_el*eff - blueData.cost

    fig.add_trace(go.Scatter(x=ocf_r*100, y=delta_cost, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=3)

    # add trace 4
    p_ng_r = np.linspace(config['plotting']['x4_min'], config['plotting']['x4_max'], config['plotting']['n_samples'])
    delta_cost = greenData.cost - (FCR * C_pl/(P_pl*flh) + p_ng_r/effb + c_CTS*emi)

    fig.add_trace(go.Scatter(x=ocf_r*100, y=delta_cost, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=4)

    # add trace 5
    C_pl_r = np.linspace(config['plotting']['x5_min'], config['plotting']['x5_max'], config['plotting']['n_samples'])
    delta_cost = greenData.cost - (FCR * C_pl_r/(P_pl*flh) + p_ng/effb + c_CTS*emi)

    fig.add_trace(go.Scatter(x=ocf_r*100, y=delta_cost, hoverinfo='skip', mode='lines', showlegend=False), row=1, col=5)

    # add horizontal line
    fig.add_hline(y=greenData.cost-blueData.cost)

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=config['labels']['x1']),
                      xaxis2=dict(title=config['labels']['x2']),
                      xaxis3=dict(title=config['labels']['x3']),
                      xaxis4=dict(title=config['labels']['x4']),
                      xaxis5=dict(title=config['labels']['x5']),
                      yaxis=dict(title=config['labels']['cost'],
                                 range=[config['plotting']['cost_min'], config['plotting']['cost_max']]))

    return fig
