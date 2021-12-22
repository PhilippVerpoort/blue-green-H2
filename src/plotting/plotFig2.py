import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


def plotFig2(fuelSpecs: dict, fuelData: pd.DataFrame, config: dict, scenario_name ="", export_img: bool = True):
    # filter data
    plotData = pd.DataFrame()
    for fuel in config['fuels']:
        plotData = plotData.append(fuelData.query(f"fuel=='{fuel}' & year=={config['year']}"), ignore_index=True)


    # produce figure
    fig = __produceFigure(plotData, fuelSpecs, config)


    # write figure to image file
    if export_img:
        fig.write_image("output/fig2" + ("_"+scenario_name if scenario_name else "") + ".png")


    return fig


def __produceFigure(plotData: pd.DataFrame, fuelSpecs: dict, config: dict):
    # add full names to dataframe
    plotData.insert(1, 'name', len(plotData)*[''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = fuelSpecs['names'][row['fuel']]


    # create figure
    fig = px.bar(
        x=plotData.index,
        y=plotData.ci,
        color=plotData.fuel,
        color_discrete_map=fuelSpecs['colours'],
    )


    # update traces (no legend, hover info)
    for trace in fig.data:
        fuel = trace['legendgroup']
        trace['showlegend'] = False
        trace['hovertemplate'] = f"<b>{fuelSpecs['names'][fuel]}</b><br>{config['yaxislabel']}: %{{y}}<extra></extra>"


    # update axis ticks
    fig.update_xaxes(tickvals=[float(i) for i in range(len(config['fuels']))],
                     ticktext=[fuelSpecs['names'][fuel] for fuel in config['fuels']])


    # add arrows
    arrowList = [
        ('natural gas', 'blue LEB'),
        ('natural gas', 'green RE'),
        ('blue LEB', 'green RE'),
    ]

    for i, arrow in enumerate(arrowList):
        fuelA, fuelB = arrow

        ciA = plotData[plotData['fuel'] == fuelA].iloc[0]['ci']
        ciB = plotData[plotData['fuel'] == fuelB].iloc[0]['ci']
        xA = config['fuels'].index(fuelA)
        xB = config['fuels'].index(fuelB)

        if i==1:
            fig.add_trace(go.Scatter(x=[xA-0.4, xB+0.4], y=[ciA, ciA], mode='lines', showlegend=False, line=dict(color='black')))
            xB -= 0.25
        elif i==2:
            fig.add_trace(go.Scatter(x=[xA-0.4, xB+0.4], y=[ciA, ciA], mode='lines', showlegend=False, line=dict(color='black')))
            xB += 0.25

        fig.add_annotation(
            x=xB,         # arrows' head
            y=ciB+0.01,   # arrows' head
            ax=xB,        # arrows' tail
            ay=ciA,       # arrows' tail
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor='black',
        )

        fig.add_annotation(
            x=xB+0.15,
            y=ciB+(ciA-ciB)/2,
            text=f"<b>{i+1}<br>P<sub>CO<sub>2</sub>, {i+1}</sub><br>Q<sub>CO<sub>2</sub>, {i+1}</sub></b>",
            align='left',
            showarrow=False,
        )


    # set plotting ranges
    fig.update_layout(
        xaxis_title='',
        yaxis_title=config['yaxislabel'],
        legend=dict(
            title='',
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor = 'rgba(255,255,255,0.7)',
        ),
    )


    return fig
