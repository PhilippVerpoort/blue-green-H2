import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.data.fuels.calc_cost import paramsCost, evalCost
from src.data.fuels.calc_ghgi import paramsGHGI, evalGHGI
from src.timeit import timeit


@timeit
def plotSensitivityFSCP(config: dict, subfigs_needed: list, is_webapp: bool = False):
    # produce figure
    fig = __produceFigure(config)

    return {'fig5': fig}


def __produceFigure(config: dict):
    # plot
    lastColWidth = 0.04
    numSensitivityPlots = len(config['sensitivity_params'])
    fig = make_subplots(
        rows=1,
        cols=numSensitivityPlots+1,
        shared_yaxes=True,
        horizontal_spacing=0.015,
        column_widths=numSensitivityPlots*[(1.0-lastColWidth)/numSensitivityPlots] + [lastColWidth],
    )


    # loop over fuels
    has_vline = []
    hasLegend = []
    allLines = {var: {'y': []} for var in config['sensitivity_params']}
    addToLegend = True

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


            # cut-off line going from infinity to minus infinity
            cutoff = 2000.0
            if j == 1 and fscp.max() > cutoff:
                fscp[:fscp.argmax()] = cutoff


            # draw lines
            fig.add_trace(
                go.Scatter(
                    x=x*settings['scale'],
                    y=fscp,
                    name=config['legend']['fscp'],
                    mode='lines',
                    showlegend=not j and addToLegend,
                    legendgroup=1,
                    line=dict(width=config['global']['lw_thin'], color=config['colours']['fscp'], dash='dash' if fid else None),
                    hovertemplate=f"<b>FSCP in {year}</b><br>{settings['label'].split('<')[0]}: %{{x:.2f}}<br>FSCP: %{{y:.2f}}<extra></extra>",
                ),
                row=1, col=j+1,
            )
            if not j:
                addToLegend = False


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
                    legendgroup=1,
                    line=dict(width=config['global']['lw_default'], color=config['colours']['fscp'], dash='dash' if fid else None),
                    marker=dict(symbol='circle-open', size=config['global']['highlight_marker_sm'], line={'width': config['global']['lw_thin'], 'color': config['colours']['fscp']},),
                    textposition=settings['textpos'][fid],
                    textfont=dict(color=config['colours']['fscp']),
                ),
                row=1, col=j+1,
            )

            if fid not in hasLegend:
                hasLegend.append(fid)


            # add vertical lines
            vlineid = f"{var}-{year}" if settings['vline'] == 'peryear' else f"{var}"
            labelheight = 0.0 + (year-2035)/5 * 0.355 if settings['vline'] == 'peryear' else 0.0
            if vlineid not in has_vline:
                fig.add_vline(
                    x=val*settings['scale'],
                    line=dict(color='black', dash='dash'),
                    row=1,
                    col=j+1
                )

                print(labelheight)
                fig.add_annotation(go.layout.Annotation(
                    text=f"Default {year}" if settings['vline'] == 'peryear' else 'Default',
                    x=val*settings['scale'],
                    xanchor='right',
                    y=config['yrange'][1]*labelheight,
                    yanchor='bottom',
                    showarrow=False,
                    textangle=270,
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
            fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(config['colours']['fscp']), .2)),
            fill='toself',
            line=dict(width=0.0),
            showlegend=False,
            legendgroup=1,
            hoverinfo='none',
        ), row=1, col=j+1)


    # add CO2 price
    co2prices_show = __getCO2Prices(config['co2price_traj'], config['years'])

    yearsInLabel = [str(y) for y in config['years']]
    yearsInLabel[-1] = 'and ' + yearsInLabel[-1]
    legendLabel = config['legend']['co2price'] + ' ' + ', '.join(yearsInLabel)

    for k, price in enumerate(co2prices_show):
        fig.add_trace(
            go.Scatter(
                x=[0.0, 3.0],
                y=2*[price['default']],
                name=legendLabel,
                showlegend=not k,
                legendgroup=2,
                mode='lines',
                line=dict(width=config['global']['lw_thin'], color=config['colours']['co2price']),
                hovertemplate=f"<b>FSCP in {year}</b><br>{settings['label'].split('<')[0]}: %{{x:.2f}}<br>FSCP: %{{y:.2f}}<extra></extra>",
            ),
            row=1,
            col=numSensitivityPlots+1,
        )

        fig.add_trace(
            go.Scatter(
                x=[1.0],
                y=[price['default']],
                text=[config['years'][k]],
                showlegend=False,
                legendgroup=2,
                hoverinfo='skip',
                mode='text',
                textposition='top right',
                textfont=dict(color=config['colours']['co2price']),
            ),
            row=1,
            col=numSensitivityPlots+1,
        )

        if config['show_co2price_unc']:
            fig.add_trace(
                go.Scatter(
                    name='Uncertainty Range',
                    x=[0.0, 3.0, 3.0, 0.0],
                    y=2*[price['lower']] + 2*[price['upper']],
                    showlegend=False,
                    legendgroup=2,
                    mode='lines',
                    marker=dict(color=config['colours']['co2price']),
                    fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(config['colours']['co2price']))),
                    fill='toself',
                    line=dict(width=config['global']['lw_ultrathin']),
                    hoverinfo='none'
                ),
                row=1,
                col=numSensitivityPlots+1,
            )

    fig.update_layout(
        **{f"xaxis{numSensitivityPlots+1}": dict(
            showticklabels=False,
            title=config['lastxaxislabel'],
            tickmode='array',
            tickvals=[],
            range=[1.0, 2.0],
        ),}
    )


    # set y axis range and label
    fig.update_layout(yaxis=dict(
        title=config['ylabel'],
        range=config['yrange'],
    ))


    # update legend styling
    fig.update_layout(
        legend=dict(
            yanchor='top',
            y=-0.3,
            xanchor='left',
            x=0.0,
        ),
    )


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

    cost_diff = sum(costB[comp]['val'] for comp in costB) - sum(costA[comp]['val'] for comp in costA)
    ghgi_diff = sum(ghgiA[comp]['val'] for comp in ghgiA) - sum(ghgiB[comp]['val'] for comp in ghgiB)

    if isinstance(cost_diff, np.ndarray):
        fscp = np.maximum(cost_diff, [0.0]*len(cost_diff)) / ghgi_diff
    else:
        fscp = max(cost_diff, 0.0) / ghgi_diff

    return fscp


def __getCO2Prices(co2price_traj, years):
    co2prices_show = []

    for y in years:
        vals = [co2price_traj['values'][t][co2price_traj['years'].index(y)] for t in co2price_traj['values']]
        valUp = min(vals)
        valLo = max(vals)
        valDef = next(v for v in vals if v not in [valUp, valLo])

        co2prices_show.append({
            'upper': valUp,
            'lower': valLo,
            'default': valDef,
        })

    return co2prices_show
