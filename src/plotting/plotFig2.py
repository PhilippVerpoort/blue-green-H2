import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from src.plotting.img_export_cfg import getFontSize, getImageSize


def plotFig2(fuelSpecs: dict, fuelData: pd.DataFrame,
             config: dict, export_img: bool = True):
    # filter data
    plotData = pd.DataFrame()
    for fuel in config['fuels']:
        plotData = plotData.append(fuelData.query(f"fuel=='{fuel}' & year=={config['year']}"), ignore_index=True)


    # produce figure
    fig = __produceFigure(plotData, fuelSpecs, config)


    # write figure to image file
    if export_img:
        w_mm = 88.0
        h_mm = 81.0

        fs = getFontSize(5.0)

        fig.update_layout(font_size=fs)
        fig.update_annotations(font_size=fs)
        fig.update_xaxes(title_font_size=fs,
                         tickfont_size=fs)
        fig.update_yaxes(title_font_size=fs,
                         tickfont_size=fs)

        fig.write_image("output/fig2.png", **getImageSize(w_mm, h_mm))


    return fig


def __produceFigure(plotData: pd.DataFrame, fuelSpecs: dict, config: dict):
    # add full names to dataframe
    plotData.insert(1, 'name', len(plotData)*[''])
    for i, row in plotData.iterrows():
        plotData.at[i, 'name'] = fuelSpecs['names'][row['fuel']]
    plotData['ci_gPkWh'] = plotData['ci']*1000


    # create figure
    fig = px.bar(
        x=plotData.index,
        y=plotData.ci_gPkWh,
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

        ciA = plotData[plotData['fuel'] == fuelA].iloc[0]['ci_gPkWh']
        ciB = plotData[plotData['fuel'] == fuelB].iloc[0]['ci_gPkWh']
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


    # update axes titles
    fig.update_layout(
        xaxis_title='',
        yaxis_title=config['yaxislabel'],
    )


    # update legend style
    fig.update_layout(
        legend=dict(
            title='',
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )


    # update axis styling
    for axis in ['xaxis', 'yaxis']:
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


    return fig
