import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.data.fuels.calc_cost import paramsCost, evalCost
from src.data.fuels.calc_ghgi import paramsGHGI, evalGHGI
from src.timeit import timeit


@timeit
def plotSensitivityFSCP(fuels: dict, config: dict, subfigs_needed: list):
    # produce figure
    fig = __produceFigure(fuels, config)

    # styling figure
    __styling(fig)

    return {'fig4': fig}


def __produceFigure(fuels: dict, config: dict):
    # plot
    fig = make_subplots(
        rows=1,
        cols=len(config['sensitivity_params']),
        shared_yaxes=True,
        horizontal_spacing=0.02
    )


    # loop over fuels
    has_vline = []
    hasLegend = []
    allLines = {var: {'y': []} for var in config['sensitivity_params']}

    for fid, fuelA, fuelB, year in [(fid, *f.split(' to '), y) for fid, f in enumerate(config['fuels']) for y in config['years']]:
        typeA = config['fuelSpecs'][fuelA]['type']
        typeB = config['fuelSpecs'][fuelB]['type']

        pars = {fuel: __getFuelPs(config['fuelSpecs'][fuel]['params'], config['fuelSpecs'][fuel]['type'], config['fuelSpecs'][fuel]['options'], year) for fuel in [fuelA, fuelB]}

        for j, item in enumerate(config['sensitivity_params'].items()):
            var, settings = item

            # get linspaces for parameters, x, and y
            x, ps, val = __calcLinspace(var, settings, config['n_samples'], *pars[fuelA], *pars[fuelB])
            fscp = __getFSCP(*ps, typeA, typeB)


            # save for creation of filled area
            allLines[var]['x'] = x
            allLines[var]['y'].append(fscp)


            # cut off line going from infinity to minus infinity
            cutoff = 2000.0
            if j == 1 and fscp.max() > cutoff:
                fscp[:fscp.argmax()] = cutoff


            # draw lines
            fig.add_trace(
                go.Scatter(
                    x=x*settings['scale'],
                    y=fscp,
                    mode='lines',
                    showlegend=False,
                    line=dict(width=config['global']['lw_thin'], color=config['colour'], dash='dash' if fid else None),
                    hovertemplate=f"<b>FSCP in {year}</b><br>{settings['label'].split('<')[0]}: %{{x:.2f}}<br>FSCP: %{{y: .2f}}<extra></extra>",
                ),
                row=1, col=j+1,
            )


            # markers and vertical lines at x=0 for mode relative
            if settings['mode'] == 'relative':
                val = 0.0


            # add markers
            fscp = __getFSCP(*pars[fuelA], *pars[fuelB], typeA, typeB)
            fig.add_trace(
                go.Scatter(
                    x=[val*settings['scale']],
                    y=[fscp],
                    text=[year],
                    hoverinfo='skip',
                    mode='markers+text',
                    showlegend=False,
                    line=dict(width=config['global']['lw_default'], color=config['colour'], dash='dash' if fid else None),
                    marker=dict(symbol='circle-open', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': config['colour']},),
                    textposition=settings['textpos'][fid],
                    textfont=dict(color=config['colour']),
                ),
                row=1, col=j+1,
            )

            if fid not in hasLegend:
                hasLegend.append(fid)


            # add vertical lines
            vlineid = f"{var}-{year}" if settings['vline'] == 'peryear' else f"{var}"
            if vlineid not in has_vline:
                fig.add_vline(
                    x=val*settings['scale'],
                    line=dict(color='black', dash='dash'),
                    row=1,
                    col=j+1
                )

                fig.add_annotation(go.layout.Annotation(
                    text=f"Default {year}" if settings['vline'] == 'peryear' else 'Default',
                    x=val*settings['scale'],
                    xanchor='left',
                    y=config['yrange'][1],
                    yanchor='top',
                    showarrow=False,
                    textangle=90,
                ), row=1, col=j+1)

                has_vline.append(vlineid)


    # set x axes ranges and labels and add area plots
    for j, item in enumerate(config['sensitivity_params'].items()):
        var, settings = item

        xrange = [settings['range'][0] * settings['scale'], settings['range'][1] * settings['scale']]

        if var == 'sh':
            xrange[-1] = 100.35

        axis = {
            'title': settings['label'],
            'range': xrange,
        }
        fig.update_layout(**{f"xaxis{j + 1 if j else ''}": axis})

        # add horizontal line for fscp=0
        fig.add_hline(0.0, row=1, col=j+1)

        # add area plots
        x = allLines[var]['x']
        yu = np.maximum.reduce(allLines[var]['y'])
        yl = np.minimum.reduce(allLines[var]['y'])

        fig.add_trace(go.Scatter(
            x=np.concatenate((x*settings['scale'], x[::-1]*settings['scale'])),
            y=np.concatenate((yu, yl[::-1])),
            mode='lines',
            fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(config['colour']), .2)),
            fill='toself',
            line=dict(width=0.0),
            showlegend=False,
            hoverinfo='none',
        ), row=1, col=j+1)


    # set y axis range and label
    fig.update_layout(yaxis=dict(
        title=config['ylabel'],
        range=config['yrange'],
    ))

    return fig


def __getFuelPs(params: pd.DataFrame, type: str, options: dict, year: int):
    pars = params.query(f"year=={year}").droplevel(level=1)

    pC = paramsCost(pars, type, options)
    pG = paramsGHGI(pars, type, options)

    return pC, pG


def __calcLinspace(var, settings, n, *ps):
    ps = list(ps)

    x = np.linspace(*settings['range'], n)

    for k in [i for i in range(4) if var in ps[i]]:
        val = ps[k][var]
        hasUncertainty = isinstance(val, tuple)

        if hasUncertainty:
            val = val[0]

        ps[k] = ps[k].copy()

        if settings['mode'] == 'absolute':
            xplot = x
        elif settings['mode'] == 'relative':
            xplot = np.linspace(val + settings['range'][0], val + settings['range'][1], n)
        else:
            raise Exception(f"Unknown mode selected for variable {var}: {settings['mode']}")

        ps[k][var] = (xplot, 0.0, 0.0) if hasUncertainty else xplot

    return x, ps, val


def __getFSCP(pAC, pAG, pBC, pBG, typeA, typeB):
    costA = evalCost(pAC, typeA)
    ghgiA = evalGHGI(pAG, typeA)
    costB = evalCost(pBC, typeB)
    ghgiB = evalGHGI(pBG, typeB)

    cost_diff = sum(costB[comp][0] for comp in costB) - sum(costA[comp][0] for comp in costA)
    ghgi_diff = sum(ghgiA[comp][0] for comp in ghgiA) - sum(ghgiB[comp][0] for comp in ghgiB)

    if isinstance(cost_diff, np.ndarray):
        fscp = np.maximum(cost_diff, [0.0]*len(cost_diff)) / ghgi_diff
    else:
        fscp = max(cost_diff, 0.0) / ghgi_diff

    return fscp


def __styling(fig: go.Figure):
    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=1.00,
            xanchor='left',
            x=1.02,
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )


    # update axis styling
    for axis in ['xaxis', 'xaxis2', 'xaxis3', 'xaxis4', 'xaxis5', 'yaxis', 'yaxis2', 'yaxis3', 'yaxis4', 'yaxis5']:
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
