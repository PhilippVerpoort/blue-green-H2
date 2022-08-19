import pandas as pd

import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.data.fuels.calc_fuels import __calcFuel
from src.timeit import timeit


@timeit
def plotCostAndEmiOverTime(fuelData: pd.DataFrame, config: dict, subfigs_needed: list):
    # produce figures
    ret = {}
    for sub, type in [('a', 'cost'), ('b', 'ghgi')]:
        subfigName = f"fig1{sub}"

        # check if plotting is needed
        if subfigName not in subfigs_needed:
            ret.update({subfigName: None})
            continue

        # plot subfigure
        subfig = __produceFigure(fuelData, config['fuelSpecs'], {**config[type], **{'global': config['global']}}, type)

        # styling figure
        __styling(subfig)

        ret.update({subfigName: subfig})

    return ret


def __getThisData(plotData: pd.DataFrame, fuelSpecs: dict, cases: list):
    ret = []

    for c in cases:
        if c.endswith('gwpOther'):
            c = c.replace('-gwpOther', '')
            options = fuelSpecs[c]['options'].copy()
            options['gwp'] = 'gwp20' if options['gwp']=='gwp100' else 'gwp100'
            ret.append(
                pd.DataFrame.from_records(__calcFuel(fuelSpecs[c]['params'], c+'-gwpOther', fuelSpecs[c]['type'], options, plotData.year.unique()))
            )
        else:
            ret.append(
                plotData.query(f"fuel=='{c}'").reset_index(drop=True)
            )

    return pd.concat(ret)



def __produceFigure(plotData: pd.DataFrame, fuelSpecs: dict, subConfig: dict, type: str):
    scale = 1.0 if type == 'cost' else 1000.0


    # create figure
    fig = go.Figure()


    # subplot labels
    fig.add_annotation(
        showarrow=False,
        text=f"<b>{'a' if type=='cost' else 'b'}</b>",
        x=0.0,
        xanchor='left',
        xref='paper',
        y=1.2,
        yanchor='top',
        yref='paper',
    )


    for cID, corridor in subConfig['showCorridors'].items():
        corrCases = corridor['cases']
        corrColour = corridor['colour'] if 'colour' in corridor else fuelSpecs[list(corrCases.keys())[0].replace('-gwpOther', '')]['colour']

        allCases = list(corrCases.keys()) + [cExt for c in corrCases.values() for cExt in (c['extended'] if 'extended' in c else [])]
        casesColours = {c: corrCases[c.replace('-gwpOther', '')]['colour'] if 'colour' in corrCases[c] else fuelSpecs[c.replace('-gwpOther', '')]['colour'] for c in allCases}
        casesLabels = {c: f"{fuelSpecs[c.replace('-gwpOther', '')]['shortname']} ({corrCases[c]['desc']})" if 'desc' in corrCases[c] else fuelSpecs[c.replace('-gwpOther', '')]['name'] for c in allCases}

        # select data and determine max and min of corridor
        thisData = __getThisData(plotData, fuelSpecs, corrCases)

        thisData['upper'] = thisData[type] + thisData[type + '_uu']
        thisData['lower'] = thisData[type] - thisData[type + '_ul']

        thisData_max = thisData.groupby('year')['upper'].max().reset_index()
        thisData_min = thisData.groupby('year')['lower'].min().reset_index()

        # add corridor
        fig.add_trace(go.Scatter(
            # The minimum (or maximum) line needs to be added before the below area plot can be applied.
            x=thisData_min.year,
            y=thisData_min['lower']*scale,
            legendgroup=cID,
            mode='lines',
            line=dict(color=corrColour, width=subConfig['global']['lw_thin'] if subConfig['showLines'] else 0.0),
            showlegend=False,
            hoverinfo='none',
        ))

        fig.add_trace(go.Scatter(
            x=thisData_max.year,
            y=thisData_max['upper']*scale,
            fill='tonexty', # fill area between traces
            mode='lines',
            legendgroup=cID,
            line=dict(color=corrColour, width=subConfig['global']['lw_thin'] if subConfig['showLines'] else 0.0),
            fillpattern=dict(shape='/') if cID.endswith('-gwpOther') else None,
            showlegend=False,
            hoverinfo='none',
        ))

        # add lines
        for c in corrCases:
            cData = __getThisData(thisData, fuelSpecs, [c])

            fig.add_trace(go.Scatter(
                # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                x=cData.year,
                y=cData[type]*scale,
                legendgroup=c,
                mode='lines',
                name=casesLabels[c],
                line=dict(color=casesColours[c], width=subConfig['global']['lw_thin'], dash='dot' if c.endswith('-gwpOther') else None),
                showlegend=True,
                hovertemplate=f"<b>{casesLabels[c]}</b><br>Time: %{{x:.2f}}<br>{subConfig['label']}: %{{y:.2f}}<extra></extra>",
            ))


    # add label inside plot
    fig.add_annotation(
        text=subConfig['label'],
        xanchor='left',
        xref='x domain',
        x=0.01,
        yanchor='bottom',
        yref='y domain',
        y=0.025,
        showarrow=False,
        bordercolor='black',
        borderwidth=2,
        borderpad=3,
        bgcolor='white',
    )


    # set axes labels
    fig.update_layout(
        xaxis=dict(title='', zeroline=True),
        yaxis=dict(title=subConfig['yaxislabel'], zeroline=True, range=[0, subConfig['ymax']*scale]),
        legend_title='',
    )
    fig.update_yaxes(rangemode= "tozero")

    return fig


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=-0.1,
            xanchor='left',
            x=0.0,
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
