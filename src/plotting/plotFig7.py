import pandas as pd
import plotly.express as px

from src.data.calc_fuels import calcFuelData


def plotFig7(fuelSpecs: dict, scenario: dict, fullParams: pd.DataFrame,
             config: dict, scenario_name = "", export_img: bool = True):
    # obtain data
    levelisedFuelData, _ = calcFuelData(scenario['options']['times'], fullParams, scenario['fuels'], scenario['options']['gwp'], levelised=True)

    # filter data
    fuels = config['fuels']
    years = config['years']
    plotData = levelisedFuelData.query("fuel in @fuels & year in @years")

    # produce figure
    fig = __produceFigure(plotData, fuelSpecs, config)

    # write figure to image file
    if export_img:
        fig.write_image("output/fig7" + ("_"+scenario_name if scenario_name else "") + ".png")

    return fig


def __produceFigure(plotData: pd.DataFrame, fuelSpecs: dict, config: dict):
    # add names
    plotData.insert(1, 'name', len(plotData)*[''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = f"{fuelSpecs['names'][row['fuel']]} {row['year']}"

    # create figure
    fig = px.bar(plotData,
        x="name",
        y=['cost__cap_cost',
           'cost__fuel_cost',
           'cost__cts_cost'],
        color_discrete_map=config['colours'],
    )

    # make adjustments
    for trace in fig.data:
        trace['name'] = config['labels'][trace['name']]
        trace['hovertemplate'] = f"<b>{trace['name']}</b><br>Cost in EUR/MWh: %{{y}}<br>For fuel %{{x}}<extra></extra>"

    # set plotting ranges
    fig.update_layout(xaxis=dict(title=""),
                      yaxis=dict(title=config['yaxislabel']),
                      legend_title="")

    return fig
