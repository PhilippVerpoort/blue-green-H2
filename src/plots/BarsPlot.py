import pandas as pd
import plotly.graph_objects as go

from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class BarsPlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('BarsPlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        # plot data
        plot_data = self._obtain_data(outputs['fuelData'], outputs['fuelSpecs'])

        # produce figures
        ret = {}
        for sub, plot_type in [('A', 'cost'), ('B', 'ghgi')]:
            subfig_name = f"figS1{sub}"

            # check if plotting is needed
            if subfig_name not in subfig_names:
                ret.update({subfig_name: None})
                continue

            # run plot function
            fig = self._produce_figure(plot_data, self._subfig_cfgs[subfig_name], plot_type)

            # save in return dict
            ret.update({subfig_name: fig})

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _obtain_data(self, fuel_data: pd.DataFrame, fuel_specs: dict) -> pd.DataFrame:
        # filter data
        fuels = self.cfg['fuels']
        years = self.cfg['years']
        plot_data = fuel_data.query('fuel in @fuels & year in @years')

        # add names
        plot_data.insert(1, 'name', len(plot_data) * [''])
        for i, row in plot_data.iterrows():
            plot_data.at[i, 'name'] = fuel_specs[row['fuel']]['name']

        return plot_data

    def _produce_figure(self, plot_data: pd.DataFrame, plot_config: dict, plot_type: str) -> go.Figure:
        scale = 1.0 if plot_type == 'cost' else 1000.0

        # create figure
        fig = go.Figure()

        # add bars
        keys = plot_config['labels'].keys()
        for stack in keys:
            fig.add_bar(
                x=[plot_data.year, plot_data.fuel],
                y=plot_data[stack] * scale,
                marker_color=plot_config['colours'][stack],
                name=plot_config['labels'][stack],
                hovertemplate=f"<b>{plot_config['labels'][stack]}</b><br>"
                              f"{plot_config['yaxislabel']}: %{{y}}<br>"
                              f"For fuel %{{x}}<extra></extra>",
            )
        fig.update_layout(barmode='stack')

        # add error bar
        fig.add_bar(
            x=[plot_data.year, plot_data.fuel],
            y=0.00000001 * plot_data[plot_type],
            error_y=dict(
                type='data',
                array=plot_data[f"{plot_type}_uu"] * scale,
                arrayminus=plot_data[f"{plot_type}_ul"] * scale,
                color='black',
                thickness=self._styles['lw_thin'],
                width=self._styles['highlight_marker_sm'],
            ),
            showlegend=False,
        )

        # add vertical line
        n_years = plot_data['year'].nunique()
        n_fuels = plot_data['fuel'].nunique()
        for i in range(n_years - 1):
            fig.add_vline(n_fuels * (i + 1) - 0.5, line_width=0.5, line_color='black')
            fig.add_vline(n_fuels * (i + 1) - 0.5, line_width=0.5, line_color='black')

        # set axes labels
        fig.update_layout(
            xaxis=dict(title=''),
            yaxis=dict(title=plot_config['yaxislabel'], range=[0.0, plot_config['ymax'] * scale]),
            legend_title=''
        )

        return fig
