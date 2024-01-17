from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.proc_func.fscps import calc_fscps, calc_interpolate_selected_fscps
from src.proc_func.fuels import calc_fuel
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class FSCPCorridors(BasePlot):
    figs, cfg = load_yaml_plot_config_file('FSCPCorridors')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {}

        # produce figures
        for sub in list('AB'):
            subfig_name = f"figED3{sub}"

            # check if plotting is needed
            if subfig_name not in subfig_names:
                ret.update({subfig_name: None})
                continue

            # get subfigure config
            show_corridors = self._subfig_cfgs[subfig_name]['showCorridors']
            label = self._subfig_cfgs[subfig_name]['label']

            # get FSCP data
            selected_cases = {
                scid: scspecs['fuels']
                for corridor in show_corridors.values()
                for scid, scspecs in corridor['cases'].items()
            }
            plot_scatter, plot_lines = calc_interpolate_selected_fscps(outputs['fuelData'], selected_cases, self.cfg['n_samples'])
            plot_data = pd.concat(plot_lines).droplevel(-1).reset_index().rename(columns={'index': 'fuel'})

            # produce figure
            ret[subfig_name] = self._produce_figure(plot_data, show_corridors, label, outputs['fuelSpecs'])

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _produce_figure(self, plot_data: pd.DataFrame, show_corridors: dict, label: str, fuel_specs: dict):

        # create figure
        fig = go.Figure()

        # loop over the defined corridors
        for corr_id, corr_specs in show_corridors.items():
            corr_cases = corr_specs['cases']
            corr_colour = (corr_specs['colour']
                           if 'colour' in corr_specs else
                           fuel_specs[list(corr_cases.keys())[0].replace('-gwpOther', '')]['colour'])

            all_cases = list(corr_cases.keys()) + [
                c_ext for c in corr_cases.values()
                for c_ext in (c['extended'] if 'extended' in c else [])
            ]
            cases_colours = {
                c: corr_cases[c.replace('-gwpOther', '')]['colour']
                if 'colour' in corr_cases[c] else
                fuel_specs[c.replace('-gwpOther', '')]['colour']
                for c in all_cases
            }
            case_group_label = fuel_specs[all_cases[0].replace('-gwpOther', '')]['shortname']
            cases_labels = {
                c: corr_cases[c]['desc']
                if 'desc' in corr_cases[c] else
                fuel_specs[c.replace('-gwpOther', '')]['name']
                for c in all_cases
            }

            legend_id = corr_id.rstrip('-')[0]

            # select data and determine max and min of corridor
            this_data = plot_data.query(f"fuel.isin({list(corr_cases.keys())})").reset_index(drop=True)

            if self.cfg['showUnc']:
                this_data['upper'] = this_data['fscp'] + this_data['fscp' + '_uu']
                this_data['lower'] = this_data['fscp'] - this_data['fscp' + '_ul']
            else:
                this_data['upper'] = this_data['fscp']
                this_data['lower'] = this_data['fscp']

            this_data_max = this_data.groupby('year')['upper'].max().reset_index()
            this_data_min = this_data.groupby('year')['lower'].min().reset_index()

            # add corridor
            fig.add_trace(go.Scatter(
                # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                x=this_data_min.year,
                y=this_data_min['lower'],
                legendgroup=legend_id,
                mode='lines',
                line=dict(color=corr_colour, width=self._styles['lw_thin'] if self.cfg['showLines'] else 0.0),
                showlegend=False,
                hoverinfo='skip',
            ))

            fig.add_trace(go.Scatter(
                x=this_data_max.year,
                y=this_data_max['upper'],
                fill='tonexty',
                mode='lines',
                legendgroup=legend_id,
                line=dict(color=corr_colour, width=self._styles['lw_thin'] if self.cfg['showLines'] else 0.0),
                fillpattern=dict(shape='/') if corr_id.endswith('-gwpOther') else None,
                fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(corr_colour), .3)),
                showlegend=False,
                hoverinfo='skip',
            ))

            # add lines
            for case, case_specs in corr_cases.items():
                case_data = plot_data.query(f"fuel=='{case}'").reset_index(drop=True)

                fig.add_trace(go.Scatter(
                    # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                    x=case_data.year,
                    y=case_data['fscp'],
                    legendgrouptitle=dict(text=f"<b>{case_group_label}</b>"),
                    legendgroup=legend_id,
                    mode='lines',
                    name=cases_labels[case],
                    line=dict(
                        color=cases_colours[case],
                        width=self._styles['lw_thin'],
                        dash='dot' if 'dashed' in case_specs and case_specs['dashed'] else None,
                    ),
                    showlegend=True,
                    hovertemplate=f"<b>{cases_labels[case]}</b><br>"
                                  f"Year: %{{x:.2f}}<br>"
                                  f"FSCP: %{{y:.2f}}"
                                  f"<extra></extra>",
                ))

        # set axes labels
        fig.update_layout(
            xaxis=dict(title='', zeroline=True),
            yaxis=dict(title=self.cfg['yaxislabel'], zeroline=True, range=[0, self.cfg['ymax']]),
            legend_title='',
        )
        fig.update_yaxes(rangemode="tozero")

        # set legend position
        fig.update_layout(
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.15,
                xanchor='left',
                x=0.0,
            ),
            margin_b=250.0,
        )

        # add top annotation
        annotation_styling = dict(
            xanchor='center', yanchor='middle', showarrow=False,
            bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white'
        )

        for i in range(2):
            fig.add_annotation(
                x=0.50,
                xref='x domain',
                y=1.0,
                yref='y domain',
                yshift=40,
                text=label,
                **annotation_styling
            )

        return fig
