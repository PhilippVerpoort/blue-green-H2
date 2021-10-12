import yaml
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def __getPlottingConfig():
    yamlData = yaml.load(open('input/config.yml', 'r').read(), Loader=yaml.FullLoader)
    names = yamlData['names']
    colours = yamlData['colours']
    other = yamlData['other']

    return names, colours, other

def plotFig1(fuelsData: dict, FSCPData: pd.DataFrame, showFuels = None, showFSCPs = None, scenario_name = ""):
    # load config setting from YAML file
    names, colours, otherCfg = __getPlottingConfig()

    # select which lines to plot based on function argument
    if showFuels is None:
        plotData = fuelsData.query("year == 2020")
    else:
        tmp = pd.DataFrame(columns=fuelsData.keys())
        for year, fuel in showFuels:
            addFuel = fuelsData.query("year == {} & fuel == '{}'".format(year, fuel)).reset_index(drop=True)
            tmp = pd.concat([tmp, addFuel], ignore_index = True)
        plotData = tmp

    # add carbon price to plotting data
    plotData = __getFuelDataWithCP(plotData, otherCfg['carb_price_max'])

    # add full names of fuels to plotting data
    plotData = plotData.assign(name=lambda f: names[f.iloc[0].fuel])

    # axis and legend labels
    labels = {
        'fuel': "Fuel Type",
        'year': "",
        'CP': "Carbon Pricing in €/tCO2eq",
        'total_cost': "Total cost in €/MWh<sub>LHV</sub>",
    }

    # plot lines
    fig = px.line(plotData, x="CP", y="total_cost", color="fuel", line_dash="year", line_group="year",
                  color_discrete_map=colours,
                  labels=labels)

    # set names of lines in legend
    legendYear = None
    for trace in fig.data:
        print(trace)

        fuel = trace.name.split(",")[0]
        year = trace.name.split(",")[1].strip()

        trace.name = names[fuel]

        if legendYear is None: legendYear = year
        elif year != legendYear: trace.showlegend = False

    # add FSCP markers to plot
    if showFSCPs is not None:
        for year_x, fuel_x, year_y, fuel_y in showFSCPs:
            FSCPpoint = FSCPData.query("year_x=={} & fuel_x=='{}' & year_y=={} & fuel_y=='{}'".format(year_x, fuel_x, year_y, fuel_y))
            fscp = FSCPpoint.iloc[0].fscp
            fscp_tc = FSCPpoint.iloc[0].fscp_tc
            fig.add_trace(go.Scatter(x=fscp, y = fscp_tc,
                                     marker=dict(symbol='circle-open', size=12, line={'width': 2}, color='Black'),
                                     showlegend=False))
            fig.add_trace(go.Scatter(x=(fscp, ), y = FSCPpoint.fscp_tc,
                                     mode="lines",
                                     showlegend=False))

    # write figure to image file
    fig.write_image("output/fig1" + ("_"+scenario_name if scenario_name else "") + ".png")


def __getFuelDataWithCP(fuelsData: dict, carb_price_max = 1000.0):
    fuelsDatawCP = pd.concat([fuelsData.assign(CP = 0.0), fuelsData.assign(CP = carb_price_max)]).\
                      assign(total_cost = lambda f: f['cost'] + f['CP'] * f['ci']).\
                      reset_index(drop=True)

    return fuelsDatawCP