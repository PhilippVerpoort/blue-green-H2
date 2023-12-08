from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.proc_func.fuels import calc_fuel
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class CostEmiOverTimePlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('CostEmiOverTimePlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {}

        # produce figures
        for sub, plot_type in [('A', 'cost'), ('B', 'ghgi')]:
            subfig_name = f"fig1{sub}"

            # check if plotting is needed
            if subfig_name not in subfig_names:
                ret.update({subfig_name: None})
                continue

            # plot subfigure
            subcfg = self._subfig_cfgs[subfig_name]
            subfig = self._produce_figure(outputs['fuelData'], outputs['fuelSpecs'], subcfg, plot_type,
                                          inputs['params_options'])

            ret.update({subfig_name: subfig})

        if 'figS5' in subfig_names:
            plot_type = 'cost'
            subcfg = self._subfig_cfgs['fig1A'] | self._subfig_cfgs['figS5']
            ret['figS5'] = self._produce_figure(outputs['fuelData'], outputs['fuelSpecs'], subcfg, plot_type,
                                                inputs['params_options'], with_iea=True, iea_data=inputs['iea_data'],
                                                cost_h2transp=outputs['fullParams'].loc['cost_h2transp'])

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _produce_figure(self, plot_data: pd.DataFrame, fuel_specs: dict, sub_config: dict, plot_type: str,
                        params_options: dict, with_iea: bool = False, iea_data: Optional[pd.DataFrame] = None,
                        cost_h2transp: Optional[pd.DataFrame] = None):
        scale = 1.0 if plot_type == 'cost' else 1000.0

        # create figure
        fig = go.Figure()

        # loop over the defined corridors
        for corr_id, corr_specs in sub_config['showCorridors'].items():
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
            this_data = self._get_this_data(plot_data, fuel_specs, corr_cases, params_options)

            this_data['upper'] = this_data[plot_type] + this_data[plot_type + '_uu']
            this_data['lower'] = this_data[plot_type] - this_data[plot_type + '_ul']

            this_data_max = this_data.groupby('year')['upper'].max().reset_index()
            this_data_min = this_data.groupby('year')['lower'].min().reset_index()

            # add corridor
            fig.add_trace(go.Scatter(
                # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                x=this_data_min.year,
                y=this_data_min['lower']*scale,
                legendgroup=legend_id,
                mode='lines',
                line=dict(color=corr_colour, width=self._styles['lw_thin'] if sub_config['showLines'] else 0.0),
                showlegend=False,
                hoverinfo='skip',
            ))

            fig.add_trace(go.Scatter(
                x=this_data_max.year,
                y=this_data_max['upper']*scale,
                fill='tonexty',
                mode='lines',
                legendgroup=legend_id,
                line=dict(color=corr_colour, width=self._styles['lw_thin'] if sub_config['showLines'] else 0.0),
                fillpattern=dict(shape='/') if corr_id.endswith('-gwpOther') else None,
                fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(corr_colour), .3)),
                showlegend=False,
                hoverinfo='skip',
            ))

            # add lines
            for case in corr_cases:
                case_data = self._get_this_data(this_data, fuel_specs, [case], params_options)

                fig.add_trace(go.Scatter(
                    # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                    x=case_data.year,
                    y=case_data[plot_type] * scale,
                    legendgrouptitle=dict(text=f"<b>{case_group_label}</b>"),
                    legendgroup=legend_id,
                    mode='lines',
                    name=cases_labels[case],
                    line=dict(
                        color=cases_colours[case],
                        width=self._styles['lw_thin'],
                        dash='dot' if case.endswith('-gwpOther') else None,
                    ),
                    showlegend=True,
                    hovertemplate=f"<b>{cases_labels[case]}</b><br>"
                                  f"Time: %{{x:.2f}}<br>"
                                  f"{sub_config['label']}: %{{y:.2f}}"
                                  f"<extra></extra>",
                ))

        # add label inside plot
        label_pos = dict(
            xanchor='right',
            x=0.99,
            yanchor='top',
            y=0.98,
        ) if with_iea else dict(
            xanchor='left',
            x=0.01,
            yanchor='bottom',
            y=0.025,
        )
        fig.add_annotation(
            text=sub_config['label'],
            xref='x domain',
            yref='y domain',
            showarrow=False,
            bordercolor='black',
            borderwidth=2,
            borderpad=3,
            bgcolor='white',
            **label_pos,
        )

        # set axes labels
        fig.update_layout(
            xaxis=dict(title='', zeroline=True),
            yaxis=dict(title=sub_config['yaxislabel'], zeroline=True, range=[0, sub_config['ymax'] * scale]),
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

        # add IEA data
        if with_iea:
            iea_data_groups = iea_data.groupby(['technology', 'subtechnology'], dropna=False)
            for k, ((tech, subtech), rows) in enumerate(iea_data_groups):
                rows_withtnd = rows \
                    .merge(
                        cost_h2transp['val']
                        .to_frame('cost_h2transp')
                        .rename_axis('period')
                        .reset_index(),
                        on='period',
                        how='outer',
                    ) \
                    .set_index('period') \
                    .sort_index() \
                    .assign(cost_h2transp=lambda df: df['cost_h2transp'].bfill()) \
                    .dropna(subset='value') \
                    .assign(value=lambda df: df['value'] + df['cost_h2transp']) \
                    .drop(columns='cost_h2transp') \
                    .reset_index()
                plot_data = rows_withtnd \
                    .groupby('period')['value'] \
                    .agg(['mean', 'max']) \
                    .assign(delta=lambda df: df['max'] - df['mean']) \
                    .reset_index()
                colour = sub_config['iea_colours'][tech] if tech == 'Blue' else sub_config['iea_colours'][tech][subtech]
                fig.add_trace(go.Scatter(
                    y=plot_data['mean'],
                    x=plot_data['period'] + k * 0.2,
                    mode='markers',
                    error_y=dict(
                        type='data',
                        array=plot_data['delta'],
                        visible=True,
                    ),
                    marker=dict(
                        color=colour,
                        size=10.0,
                        symbol='circle',
                    ),
                    legendgroup='iea',
                    legendgrouptitle_text='<b>IEA H<sub>2</sub></b>',
                    name=(f"{tech} H<sub>2</sub>"
                          if not isinstance(subtech, str) else
                          f"{tech} H<sub>2</sub><br>({subtech})"),
                ))

            fig.update_layout(
                xaxis_range=[2021.5, 2050.0],
                yaxis_range=[0.0, sub_config['ymaxS5']],
            )

        return fig

    def _get_this_data(self, plot_data: pd.DataFrame, fuel_specs: dict, cases: list, params_options: dict):
        ret = []

        for c in cases:
            if c.endswith('gwpOther'):
                c = c.replace('-gwpOther', '')
                options = fuel_specs[c]['options'].copy()
                options['gwp'] = 'gwp20' if options['gwp'] == 'gwp100' else 'gwp100'
                ret.append(
                    pd.DataFrame.from_records(
                        calc_fuel(fuel_specs[c]['params'], c + '-gwpOther', fuel_specs[c]['type'], options,
                                  plot_data.year.unique(), params_options)
                    )
                )
            else:
                ret.append(
                    plot_data.query(f"fuel=='{c}'").reset_index(drop=True)
                )

        return pd.concat(ret)
