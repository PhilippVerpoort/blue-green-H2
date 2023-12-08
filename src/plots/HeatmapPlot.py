import copy

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class HeatmapPlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('HeatmapPlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {}
        for application in ['heating', 'steel']:
            for sub, plot_type in [('A', 'left'), ('B', 'right')]:
                subfig_name = f"fig4{sub}" if application == 'heating' else f"figS4{sub}"

                # check if plotting is needed
                if subfig_name not in subfig_names:
                    ret.update({subfig_name: None})
                    continue

                # select data
                plot_data, ref_data = self._select_plot_data(
                    outputs['fuelData'],
                    self.cfg['refFuel'][plot_type], self.cfg['refYear'][plot_type],
                    self.cfg['showFuels'][plot_type], self.cfg['showYears'],
                )

                # throw away all components
                plot_data = plot_data.drop(
                    columns=plot_data.filter(regex=r"^(cost|ghgi)(_uu|_ul)?__.*$").columns.to_list(),
                    axis=1,
                )
                ref_data = ref_data.drop(
                    index=ref_data.filter(regex=r"^(cost|ghgi)(_uu|_ul)?__.*$").keys().to_list()
                )

                # add steel data for fig S4
                if application == 'steel':
                    steel = self.cfg['steelAssumptions']

                    for t in [f"{comp}_{unc}" for comp in ['cost', 'ghgi'] for unc in ['uu', 'ul']]:
                        plot_data[t] *= steel['idreaf_demand_h2']
                    plot_data['cost'] += steel['idreaf_cost']

                    ref_data['cost'] = steel['bfbof_cost']
                    ref_data['ghgi'] = steel['bfbof_ghgi']

                # define plotly figure
                fig = go.Figure()

                # produce figures
                fig = self._produce_figure(fig, plot_data, ref_data, outputs['fuelSpecs'], plot_type, application)

                ret.update({subfig_name: fig})

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _select_plot_data(self, fuels_data: pd.DataFrame, ref_fuel: str, ref_year: int, show_fuels: list,
                          show_years: list):
        plot_data = fuels_data.query('fuel in @show_fuels and year in @show_years')
        ref_data = fuels_data.query(f"fuel=='{ref_fuel}' & year=={ref_year}").iloc[0]

        return plot_data, ref_data

    def _produce_figure(self, fig: go.Figure, plot_data: pd.DataFrame, ref_data: pd.Series, fuel_specs: dict,
                        plot_type: str, application: str):
        config = self.cfg

        # apply scaling
        if application == 'heating':
            config = copy.deepcopy(config)
            plot_data = plot_data.copy()
            ref_data = ref_data.copy()

            config['plotting'][application]['ghgi_max'] *= 1000.0
            plot_data[['ghgi', 'ghgi_uu', 'ghgi_ul']] *= 1000.0
            ref_data[['ghgi', 'ghgi_uu', 'ghgi_ul']] *= 1000.0

        # configure FSCP plotting
        fscp_conf = {
            'ghgi_min': 0.0,
            'ghgi_max': config['plotting'][application]['ghgi_max'],
            'cost_min': 0.0,
            'cost_max': config['plotting'][application]['cost_max'],
            'fscp_scaling': 1000.0 if application == 'heating' else 1.0,
            'zmax': config['plotting'][application]['zmax'],
            'zdticks': config['plotting'][application]['zdticks'],
            'zdeltalines': config['plotting'][application]['zdeltalines'],
            'n_samples': config['plotting']['n_samples'],
            'colorbarTitle': ('<i>FSCP</i><sub>NG→H<sub>2</sub></sub>'
                              if application == 'heating' else
                              '<i>FSCP</i><sub>BF-BOF→H<sub>2</sub>-DR</sub>'),
        }

        # add line traces
        traces = self._add_line_traces(plot_data, fuel_specs, config)
        for trace in traces:
            fig.add_trace(trace)

        # add FSCP traces
        traces = self._add_fscp_traces(ref_data, config['thickLines'][application][plot_type], fscp_conf,
                                       self._styles['lw_thin'], self._styles['lw_ultrathin'], plot_type == 'right')
        for trace in traces:
            fig.add_trace(trace)

        # determine y-axis plot range
        shift = 0.1
        ylow = (0.0
                if application == 'heating' else
                ref_data.cost - shift * (config['plotting']['steel']['cost_max'] - ref_data.cost))

        # set plotting ranges
        fig.update_layout(
            xaxis=dict(
                title=config['labels'][application]['ghgi'],
                range=[0.0, config['plotting'][application]['ghgi_max']],
            ),
            yaxis=dict(
                title=config['labels'][application]['cost'],
                range=[ylow, config['plotting'][application]['cost_max']],
            ),
            margin_t=160.0,
            margin_r=200.0,
        )

        # add text annotations explaining figure content
        annotation_styling_a = dict(xanchor='center', yanchor='bottom', showarrow=False,
                                    bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

        fig.add_annotation(
            x=0.50,
            xref='x domain',
            y=1.0,
            yref='y domain',
            yshift=20.0,
            text=config['annotationLabels'][plot_type],
            **annotation_styling_a,
        )

        annotation_styling_b = dict(xanchor='left', yanchor='top', showarrow=False)
        fig.add_annotation(
            x=0.01*config['plotting'][application]['ghgi_max'],
            y=ref_data.cost,
            xref='x', yref='y', text=config['baselineLabels'][application],
            **annotation_styling_b,
        )

        # set legend position
        fig.update_layout(
            legend=dict(
                yanchor='top',
                y=-0.2,
                xanchor='left',
                x=0.0,
            ),
        )

        return fig

    def _add_line_traces(self, plot_data: pd.DataFrame, fuel_specs: dict, config: dict):
        traces = []
        has_legend = []

        for fuel in plot_data.fuel.unique():
            # line properties
            descs = [
                'progressive' if 'prog' in fuel else 'conservative',
                'low supply-chain CO<sub>2</sub>' if fuel.endswith('lowscco2') else None,
            ]
            name = fuel_specs[fuel]['name'].split(' (')[0] + f" ({', '.join([d for d in descs if d])})"
            col = fuel_specs[fuel]['colour']
            tech = fuel
            dashed = any(t in fuel for t in config['tokensDashed'])

            # data
            this_data = plot_data.query(f"fuel=='{fuel}'")

            # points and lines
            traces.append(go.Scatter(
                x=this_data.ghgi,
                y=this_data.cost,
                text=this_data.year if not fuel.endswith('lowscco2') else None,
                textposition='top left' if 'pess' in fuel else 'bottom right',
                textfont=dict(color=col),
                name=name,
                legendgroup=fuel,
                showlegend=False,
                mode='markers+text',
                line=dict(color=col),
                marker_size=self._styles['highlight_marker_sm'],
                hoverinfo='skip',
            ))

            traces.append(go.Scatter(
                x=this_data.ghgi,
                y=this_data.cost,
                name=name,
                legendgroup=tech,
                showlegend=tech not in has_legend,
                line=dict(color=col, width=self._styles['lw_default'], dash='dot' if dashed else 'solid'),
                mode='lines',
                hoverinfo='skip',
            ))

            if tech not in has_legend:
                has_legend.append(tech)

            # hover template
            traces.append(go.Scatter(
                x=this_data.ghgi,
                y=this_data.cost,
                error_x=dict(type='data', array=this_data.ghgi_uu, arrayminus=this_data.ghgi_ul, thickness=0.0),
                error_y=dict(type='data', array=this_data.cost_uu, arrayminus=this_data.cost_ul, thickness=0.0),
                line_color=col,
                showlegend=False,
                mode='lines',
                line_width=0.000001,
                customdata=this_data.year,
                hovertemplate=f"<b>{name}</b><br>Year: %{{customdata}}<br>"
                              f"Carbon intensity: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                              f"Direct cost: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}"
                              f"<extra></extra>",
            ))

            # error bars
            this_data = this_data.query(f"year==[2025,2030,2040,2050]")
            traces.append(go.Scatter(
                x=this_data.ghgi,
                y=this_data.cost,
                error_x=dict(
                    type='data',
                    array=this_data.ghgi_uu,
                    arrayminus=this_data.ghgi_ul,
                    thickness=self._styles['lw_thin'],
                ),
                error_y=dict(
                    type='data',
                    array=this_data.cost_uu,
                    arrayminus=this_data.cost_ul,
                    thickness=self._styles['lw_thin'],
                ),
                line_color=col,
                marker_size=0.000001,
                showlegend=False,
                mode='markers',
                customdata=this_data.year,
                hoverinfo='skip',
            ))

        return traces

    def _add_fscp_traces(self, ref_data: pd.Series, thick_lines: list, fscp_conf: dict, lw_thin: float,
                         lw_ultrathin: float, showscale: bool):
        traces = []

        ghgi_samples = np.linspace(fscp_conf['ghgi_min'], fscp_conf['ghgi_max'], fscp_conf['n_samples'])
        cost_samples = np.linspace(fscp_conf['cost_min'], fscp_conf['cost_max'], fscp_conf['n_samples'])
        ghgi_v, cost_v = np.meshgrid(ghgi_samples, cost_samples)

        ghgi_ref = ref_data.ghgi
        cost_ref = ref_data.cost

        fscp = (cost_v - cost_ref) / (ghgi_ref - ghgi_v) * fscp_conf['fscp_scaling']

        # heatmap
        tickvals = [fscp_conf['zdticks'] * i for i in range(int(fscp_conf['zmax'] / fscp_conf['zdticks']) + 1)]
        ticktext = [str(v) for v in tickvals]
        ticktext[0] = f"≤ {ticktext[0]}"
        ticktext[-1] = f"≥ {ticktext[-1]}"
        traces.append(go.Heatmap(
            x=ghgi_samples, y=cost_samples, z=fscp,
            zsmooth='best', hoverinfo='skip',
            zmin=0.0, zmax=fscp_conf['zmax'],
            colorscale=[
                [0.0, '#c6dbef'],
                [1.0, '#f7bba1'],
            ],
            colorbar=dict(
                x=1.05,
                y=0.25,
                len=0.5,
                title=fscp_conf['colorbarTitle'],
                titleside='top',
                tickvals=tickvals,
                ticktext=ticktext,
            ),
            showscale=showscale,
        ))

        # thin lines every 50
        traces.append(go.Contour(x=ghgi_samples, y=cost_samples, z=fscp,
                                 showscale=False, contours_coloring='lines', hoverinfo='skip',
                                 colorscale=[
                                     [0.0, '#000000'],
                                     [1.0, '#000000'],
                                 ],
                                 line_width=lw_ultrathin,
                                 contours=dict(
                                     showlabels=False,
                                     start=0,
                                     end=3000,
                                     size=fscp_conf['zdeltalines'],
                                 )))

        # zero line
        traces.append(go.Contour(x=ghgi_samples, y=cost_samples, z=fscp,
                                 showscale=False, contours_coloring='lines', hoverinfo='skip',
                                 colorscale=[
                                     [0.0, '#000000'],
                                     [1.0, '#000000'],
                                 ],
                                 contours=dict(
                                     showlabels=True,
                                     start=0,
                                     end=10,
                                     size=100,
                                 ),
                                 line=dict(width=lw_thin, dash='dash')))

        # thick lines
        for kwargs in thick_lines:
            traces.append(go.Contour(
                x=ghgi_samples, y=cost_samples, z=fscp,
                showscale=False, contours_coloring='lines', hoverinfo='skip',
                colorscale=[
                    [0.0, '#000000'],
                    [1.0, '#000000'],
                ],
                line_width=lw_thin,
                contours=dict(
                    showlabels=True,
                    labelfont=dict(
                        color='black',
                    ),
                    **kwargs,
                )))

        return traces
