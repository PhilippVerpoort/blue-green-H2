import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb

from src.proc_func.cost import eval_cost, params_cost
from src.proc_func.ghgi import eval_ghgi, params_ghgi
from src.proc_func.helper import ParameterHandler
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class SensitivityPlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('SensitivityPlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        if 'fig5' not in subfig_names and 'figS7' not in subfig_names:
            return {}
        ret = {}

        # produce fig5
        ret['fig5'] = (
            self._produce_figure(inputs, outputs, self._subfig_cfgs['fig5']['fuels'])
            if 'fig5' in subfig_names else None
        )

        # produce figS7
        ret['figS7'] = (
            self._produce_figure(inputs, outputs, self._subfig_cfgs['figS7']['fuels'])
            if 'figS7' in subfig_names else None
        )

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _produce_figure(self, inputs: dict, outputs: dict, fuels: list[str]):
        # plot
        last_col_width = 0.04
        num_sensitivity_plots = len(self.cfg['sensitivity_params'])
        fig = make_subplots(
            rows=1,
            cols=num_sensitivity_plots + 1,
            shared_yaxes=True,
            horizontal_spacing=0.015,
            column_widths=num_sensitivity_plots * [(1.0 - last_col_width) / num_sensitivity_plots] + [last_col_width],
        )

        # loop over fuels
        has_vline = []
        has_legend = []
        all_lines = {var: {'y': []} for var in self.cfg['sensitivity_params']}
        add_to_legend = True

        for fid, fuel_a, fuel_b, year in [(fid, *f.split(' to '), y)
                                          for fid, f in enumerate(fuels)
                                          for y in self.cfg['years']]:
            type_a = outputs['fuelSpecs'][fuel_a]['type']
            type_b = outputs['fuelSpecs'][fuel_b]['type']

            pars = {
                fuel: _get_fuel_pars(
                    outputs['fuelSpecs'][fuel]['params'],
                    outputs['fuelSpecs'][fuel]['type'],
                    outputs['fuelSpecs'][fuel]['options'],
                    year, inputs['params_options']
                ) for fuel in [fuel_a, fuel_b]
            }

            for j, item in enumerate(self.cfg['sensitivity_params'].items()):
                var, settings = item

                # get linspaces for parameters, x, and y
                x, ps, val = _calc_linspace(var, settings, self.cfg['n_samples'], *pars[fuel_a], *pars[fuel_b])
                fscp = _get_fscp(*ps, type_a, type_b)

                # save for creation of filled area
                all_lines[var]['x'] = x
                all_lines[var]['y'].append(fscp)

                # cut-off line going from infinity to minus infinity
                cutoff = 2000.0
                if j == 1 and fscp.max() > cutoff:
                    fscp[:fscp.argmax()] = cutoff

                # draw lines
                fig.add_trace(
                    go.Scatter(
                        x=x * settings['scale'],
                        y=fscp,
                        name=self.cfg['legend']['fscp'],
                        mode='lines',
                        showlegend=not j and add_to_legend,
                        legendgroup=1,
                        line=dict(width=self._styles['lw_thin'], color=self.cfg['colours']['fscp'],
                                  dash='dash' if fid else None),
                        hovertemplate=f"<b>FSCP in {year}</b><br>"
                                      f"{settings['label'].split('<')[0]}: %{{x:.2f}}<br>"
                                      f"FSCP: %{{y:.2f}}"
                                      f"<extra></extra>",
                    ),
                    row=1,
                    col=j + 1,
                )
                if not j:
                    add_to_legend = False

                # markers and vertical lines at x=0 for mode relative
                if settings['mode'] == 'relative':
                    val = 0.0

                # add markers
                fscp = _get_fscp(*pars[fuel_a], *pars[fuel_b], type_a, type_b)
                fig.add_trace(
                    go.Scatter(
                        x=[val * settings['scale']],
                        y=[fscp],
                        text=[year],
                        hoverinfo='skip',
                        mode='markers+text',
                        showlegend=False,
                        legendgroup=1,
                        line=dict(
                            width=self._styles['lw_default'],
                            color=self.cfg['colours']['fscp'],
                            dash='dash' if fid else None,
                        ),
                        marker=dict(
                            symbol='circle-open',
                            size=self._styles['highlight_marker_sm'],
                            line={'width': self._styles['lw_thin'], 'color': self.cfg['colours']['fscp']},
                        ),
                        textposition=settings['textpos'][fid],
                        textfont_color=self.cfg['colours']['fscp'],
                    ),
                    row=1,
                    col=j + 1,
                )

                if fid not in has_legend:
                    has_legend.append(fid)

                # add vertical lines
                vlineid = f"{var}-{year}" if settings['vline'] == 'peryear' else f"{var}"
                labelheight = 0.0 + (year - 2035) / 5 * 0.355 if settings['vline'] == 'peryear' else 0.0
                if vlineid not in has_vline:
                    fig.add_vline(
                        x=val * settings['scale'],
                        line=dict(color='black', dash='dash'),
                        row=1,
                        col=j + 1
                    )

                    fig.add_annotation(
                        go.layout.Annotation(
                            text=f"Default {year}" if settings['vline'] == 'peryear' else 'Default',
                            x=val * settings['scale'],
                            xanchor='right',
                            y=self.cfg['yrange'][1] * labelheight,
                            yanchor='bottom',
                            showarrow=False,
                            textangle=270,
                        ),
                        row=1,
                        col=j + 1,
                    )

                    has_vline.append(vlineid)

        # set x axes ranges and labels and add area plots
        for j, item in enumerate(self.cfg['sensitivity_params'].items()):
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
            fig.add_hline(0.0, row=1, col=j + 1)

            # add area plots
            x = all_lines[var]['x']
            yu = np.maximum.reduce(all_lines[var]['y'])
            yl = np.minimum.reduce(all_lines[var]['y'])

            fig.add_trace(
                go.Scatter(
                    x=np.concatenate((x * settings['scale'], x[::-1] * settings['scale'])),
                    y=np.concatenate((yu, yl[::-1])),
                    mode='lines',
                    fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(self.cfg['colours']['fscp']), .2)),
                    fill='toself',
                    line=dict(width=0.0),
                    showlegend=False,
                    legendgroup=1,
                    hoverinfo='skip',
                ),
                row=1,
                col=j + 1,
            )

        # add CO2 price
        co2prices_show = _get_co2_prices(self._glob_cfg['co2price_traj'], self.cfg['years'])

        years_in_label = [str(y) for y in self.cfg['years']]
        years_in_label[-1] = 'and ' + years_in_label[-1]
        legend_label = self.cfg['legend']['co2price'] + ' ' + ', '.join(years_in_label)

        for k, price in enumerate(co2prices_show):
            fig.add_trace(
                go.Scatter(
                    x=[0.0, 3.0],
                    y=2 * [price['default']],
                    name=legend_label,
                    showlegend=not k,
                    legendgroup=2,
                    hoverinfo='skip',
                    mode='lines',
                    line=dict(width=self._styles['lw_thin'], color=self.cfg['colours']['co2price']),
                ),
                row=1,
                col=num_sensitivity_plots + 1,
            )

            fig.add_trace(
                go.Scatter(
                    x=[1.0],
                    y=[price['default']],
                    text=[self.cfg['years'][k]],
                    showlegend=False,
                    legendgroup=2,
                    hoverinfo='skip',
                    mode='text',
                    textposition='top right',
                    textfont=dict(color=self.cfg['colours']['co2price']),
                ),
                row=1,
                col=num_sensitivity_plots + 1,
            )

            if self.cfg['show_co2price_unc']:
                fig.add_trace(
                    go.Scatter(
                        name='Uncertainty Range',
                        x=[0.0, 3.0, 3.0, 0.0],
                        y=2 * [price['lower']] + 2 * [price['upper']],
                        showlegend=False,
                        legendgroup=2,
                        hoverinfo='skip',
                        mode='lines',
                        marker=dict(color=self.cfg['colours']['co2price']),
                        fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(self.cfg['colours']['co2price']))),
                        fill='toself',
                        line=dict(width=self._styles['lw_ultrathin']),
                    ),
                    row=1,
                    col=num_sensitivity_plots + 1,
                )

        fig.update_layout(
            **{f"xaxis{num_sensitivity_plots + 1}": dict(
                showticklabels=False,
                title=None,
                tickmode='array',
                tickvals=[],
                range=[1.0, 2.0],
            ), }
        )
        fig.add_annotation(
            x=2.0,
            xref=f"x{num_sensitivity_plots + 1}",
            xanchor='right',
            y=-0.185,
            yref='paper',
            yanchor='middle',
            showarrow=False,
            text=self.cfg['lastxaxislabel'],
        )

        # set y axis range and label
        fig.update_layout(yaxis=dict(
            title=self.cfg['ylabel'],
            range=self.cfg['yrange'],
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


def _get_fuel_pars(params: pd.DataFrame, fuel_type: str, options: dict, year: int, params_options: dict):
    current_params = params.query(f"year=={year}").droplevel(level=1)
    param_handler = ParameterHandler(current_params, params_options)

    p_c = params_cost(param_handler, fuel_type, options)
    p_g = params_ghgi(param_handler, fuel_type, options)

    return p_c, p_g


def _calc_linspace(var, settings, n, *ps):
    ps = list(ps)

    x = np.linspace(*settings['range'], n)

    for k in [i for i in range(4) if var in ps[i]]:
        val = ps[k][var]
        has_uncertainty = isinstance(val, tuple)

        if has_uncertainty:
            val = val[0]

        ps[k] = ps[k].copy()

        if settings['mode'] == 'absolute':
            xplot = x
        elif settings['mode'] == 'relative':
            xplot = np.linspace(val + settings['range'][0], val + settings['range'][1], n)
        else:
            raise Exception(f"Unknown mode selected for variable {var}: {settings['mode']}")

        ps[k][var] = (xplot, 0.0, 0.0) if has_uncertainty else xplot

    return x, ps, val


def _get_fscp(p_ac, p_ag, p_bc, p_bg, type_a, type_b):
    cost_a = eval_cost(p_ac, type_a)
    ghgi_a = eval_ghgi(p_ag, type_a)
    cost_b = eval_cost(p_bc, type_b)
    ghgi_b = eval_ghgi(p_bg, type_b)

    cost_diff = sum(cost_b[comp]['val'] for comp in cost_b) - sum(cost_a[comp]['val'] for comp in cost_a)
    ghgi_diff = sum(ghgi_a[comp]['val'] for comp in ghgi_a) - sum(ghgi_b[comp]['val'] for comp in ghgi_b)

    if isinstance(cost_diff, np.ndarray):
        fscp = np.maximum(cost_diff, [0.0] * len(cost_diff)) / ghgi_diff
    else:
        fscp = max(cost_diff, 0.0) / ghgi_diff

    return fscp


def _get_co2_prices(co2price_traj, years):
    co2prices_show = []

    for y in years:
        vals = [co2price_traj['values'][t][co2price_traj['years'].index(y)] for t in co2price_traj['values']]
        val_up = min(vals)
        val_lo = max(vals)
        val_def = next(v for v in vals if v not in [val_up, val_lo])

        co2prices_show.append({
            'upper': val_up,
            'lower': val_lo,
            'default': val_def,
        })

    return co2prices_show
