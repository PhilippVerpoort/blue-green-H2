import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.proc_func.cost import get_cost_blue, get_cost_green, calc_cost
from src.proc_func.ghgi import get_ghgi_blue, get_ghgi_green, get_ghgi_params_green, get_ghgi_params_blue
from src.proc_func.helper import ParameterHandler
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class BlueGreenPlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('BlueGreenPlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {
            'figED1': self._produce_figure_full(outputs['fuelSpecs'], outputs['fuelData'], inputs['params_options'])
            if 'figED1' in subfig_names else None
        }

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _produce_figure_full(self, fuel_specs: dict, fuel_data: pd.DataFrame, params_options: dict):
        # plot
        fig = make_subplots(
            rows=2,
            cols=4,
            specs=[
                [{"rowspan": 2, "colspan": 2}, None, {}, {}],
                [None, None, {}, {}],
            ],
            horizontal_spacing=0.02,
            vertical_spacing=self.cfg['vertical_spacing'],
            shared_yaxes=True,
        )

        rowcol_mapping = [
            dict(row=1, col=1),
            dict(row=1, col=3),
            dict(row=1, col=4),
            dict(row=2, col=3),
            dict(row=2, col=4),
        ]

        calced_ranges = {}

        # get colour scale config
        zmin, zmax, colourscale = self._get_colour_scale()

        # add FSCP traces for main plot (part a)
        traces = self._add_fscp_contours(zmin, zmax, colourscale)
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[0])

        # add scatter curves for main plot (part a)
        traces = self._add_fscp_scatter_curves(fuel_data)
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[0])

        # add FSCP traces in subplots
        xmin, xmax = self.cfg['plotting']['xaxis2_min'], self.cfg['plotting']['xaxis2_max']
        traces, calced_ranges['xaxis7'], calced_ranges['xaxis12'], annotations_top, shapes_top = (
            self._add_fscp_subplot_contours_top(
                fuel_specs, self.cfg['fuelBlueLeft'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax,
                colourscale, self.cfg['linedensity']['plot2'], self.cfg['plotting']['yaxis2_min'], params_options)
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[1])
        for a in annotations_top:
            a.update(dict(
                xref='x2',
                yref='y2',
                axref='x2',
                ayref='y2',
            ))
            fig.add_annotation(a, **rowcol_mapping[1])
        for s in shapes_top:
            s.update(dict(
                xref='x2',
                yref='y2',
            ))
            fig.add_shape(s, **rowcol_mapping[1])

        xmin, xmax = self.cfg['plotting']['xaxis3_min'], self.cfg['plotting']['xaxis3_max']
        traces, calced_ranges['xaxis8'], calced_ranges['xaxis13'], annotations_top, shapes_top = (
            self._add_fscp_subplot_contours_top(
                fuel_specs, self.cfg['fuelBlueRight'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax,
                colourscale, self.cfg['linedensity']['plot3'], self.cfg['plotting']['yaxis2_min'], params_options)
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[2])
        for a in annotations_top:
            a.update(dict(
                xref='x3',
                yref='y3',
                axref='x3',
                ayref='y3',
            ))
            fig.add_annotation(a, **rowcol_mapping[2])
        for s in shapes_top:
            s.update(dict(
                xref='x3',
                yref='y3',
            ))
            fig.add_shape(s, **rowcol_mapping[2])

        xmin, xmax = self.cfg['plotting']['xaxis4_min'], self.cfg['plotting']['xaxis4_max']
        traces, calced_ranges['xaxis9'], calced_ranges['xaxis14'] = self._add_fscp_subplot_contours_bottom(
            fuel_specs, self.cfg['fuelBlueLeft'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax, colourscale,
            self.cfg['linedensity']['plot4'], params_options,
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[3])

        xmin, xmax = self.cfg['plotting']['xaxis5_min'], self.cfg['plotting']['xaxis5_max']
        traces, calced_ranges['xaxis10'], calced_ranges['xaxis15'] = self._add_fscp_subplot_contours_bottom(
            fuel_specs, self.cfg['fuelBlueRight'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax, colourscale,
            self.cfg['linedensity']['plot5'], params_options,
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[4])

        # add white annotation labels
        annotation_styling = dict(x=0.01, y=0.985, xanchor='left', yanchor='top', showarrow=False, bordercolor='black',
                                  borderwidth=2, borderpad=3, bgcolor='white')
        for k, f in enumerate(['fuelBlueLeft', 'fuelBlueRight'] * 2):
            t = ('Conservative' if self.cfg[f].endswith('cons') else 'Progressive') + ' to ' + (
                'conservative' if self.cfg['fuelGreen'].endswith('cons') else 'progressive')
            fig.add_annotation(xref=f"x{k + 2} domain", yref=f"y{k + 2} domain", text=t, **annotation_styling)

        # add dummy traces to make additional x axes show
        fig.add_trace(go.Scatter(x=[1.0], y=[100], showlegend=False), row=1, col=3)
        fig['data'][-1]['xaxis'] = 'x7'
        fig.add_trace(go.Scatter(x=[2.0], y=[100], showlegend=False), row=1, col=4)
        fig['data'][-1]['xaxis'] = 'x8'
        # fig.add_trace(go.Scatter(x=[3.0], y=[100], showlegend=False), row=2, col=3)
        # fig['data'][-1]['xaxis'] = 'x9'
        # fig.add_trace(go.Scatter(x=[4.0], y=[100], showlegend=False), row=2, col=4)
        # fig['data'][-1]['xaxis'] = 'x10'
        fig.add_trace(go.Scatter(x=[5.0], y=[100], showlegend=False), row=1, col=3)
        fig['data'][-1]['xaxis'] = 'x12'
        fig.add_trace(go.Scatter(x=[6.0], y=[100], showlegend=False), row=1, col=4)
        fig['data'][-1]['xaxis'] = 'x13'
        fig.add_trace(go.Scatter(x=[7.0], y=[100], showlegend=False), row=2, col=3)
        fig['data'][-1]['xaxis'] = 'x14'
        fig.add_trace(go.Scatter(x=[8.0], y=[100], showlegend=False), row=2, col=4)
        fig['data'][-1]['xaxis'] = 'x15'

        # set y axes titles and ranges
        fig.update_yaxes(title='', range=[self.cfg['plotting']['yaxis2_min'], self.cfg['plotting']['yaxis2_max']])
        fig.update_yaxes(title=self.cfg['labels']['yaxis1'],
                         range=[self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max']],
                         ticks='outside',
                         row=1, col=1)
        fig.update_yaxes(ticks='outside', row=1, col=3)
        fig.update_yaxes(ticks='outside', row=2, col=3)

        # set x axes titles and ranges
        new_axes = self._get_xaxis_styles(calced_ranges)
        fig.update_layout(**new_axes)

        # set legend position
        fig.update_layout(
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.2,
                xanchor='left',
                x=0.0,
            ),
        )

        return fig

    def _add_fscp_contours(self, zmin: float, zmax: float, colourscale: list):
        traces = []

        delta_ghgi = np.linspace(self.cfg['plotting']['xaxis1_min'], self.cfg['plotting']['xaxis1_max'],
                                 self.cfg['plotting']['n_samples'])
        delta_cost = np.linspace(self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max'],
                                 self.cfg['plotting']['n_samples'])
        delta_ghgi_v, delta_cost_v = np.meshgrid(delta_ghgi, delta_cost)
        fscp = delta_cost_v / (delta_ghgi_v + 1.E-127)

        traces.append(go.Heatmap(x=delta_ghgi * 1000, y=delta_cost, z=fscp,
                                 zsmooth='best', showscale=True, hoverinfo='skip',
                                 zmin=zmin, zmax=zmax,
                                 colorscale=colourscale,
                                 colorbar=dict(
                                     x=1.0,
                                     y=0.4,
                                     len=0.8,
                                     title='<i>FSCP</i><sub>Blue→Green</sub>',
                                     titleside='top',
                                 )))

        traces.append(go.Contour(x=delta_ghgi * 1000, y=delta_cost, z=fscp,
                                 showscale=False, contours_coloring='lines', hoverinfo='skip',
                                 colorscale=[
                                     [0.0, '#000000'],
                                     [1.0, '#000000'],
                                 ],
                                 line_width=self._styles['lw_ultrathin'],
                                 contours=dict(
                                     showlabels=True,
                                     labelformat='.4',
                                     start=zmin,
                                     end=zmax,
                                     size=self.cfg['linedensity']['plot1'],
                                 )))

        return traces

    def _add_fscp_scatter_curves(self, fuel_data: pd.DataFrame):
        traces = []

        col_index = 0
        for fuel_blue, fuel_green in [(fb, fg)
                                      for fb in self.cfg['fuelsScatterBlue']
                                      for fg in self.cfg['fuelsScatterGreen']]:
            this_data = _convert_fuel_data(fuel_data, fuel_blue, fuel_green)

            name = ('Conservative' if 'cons' in fuel_blue else 'Progressive') + ' to ' + (
                'conservative' if 'cons' in fuel_green else 'progressive')
            legendgrouptitle = 'Low gas price' if 'low' in fuel_blue else 'High gas price'
            col = self.cfg['fscp_colour'][fuel_blue.split('-')[-1] + '-' + fuel_green.split('-')[-1]]
            col_index += 1

            # markers
            traces.append(go.Scatter(
                x=this_data.delta_ghgi * 1000,
                y=this_data.delta_cost,
                text=this_data.year,
                textposition="top right",
                textfont=dict(color=col),
                name=name,
                legendgroup='low' if 'low' in fuel_blue else 'high',
                legendgrouptitle=dict(text=f"<b>{legendgrouptitle}</b>"),
                showlegend=True,
                line=dict(color=col, width=self._styles['lw_default'], dash='dot' if 'low' in fuel_blue else None),
                mode='lines',
                hoverinfo='skip',
            ))

            # lines
            traces.append(go.Scatter(
                x=this_data.delta_ghgi * 1000,
                y=this_data.delta_cost,
                legendgroup='low' if 'low' in fuel_blue else 'high',
                showlegend=False,
                line=dict(color=col, width=self._styles['lw_default']),
                marker_size=self._styles['highlight_marker_sm'],
                mode='markers',
                hoverinfo='skip',
            ))

            # year text
            text_data = this_data.query(f"year in {self.cfg['showYearNumbers']}")
            traces.append(go.Scatter(
                x=text_data.delta_ghgi * 1000,
                y=text_data.delta_cost,
                text=text_data.year,
                textposition="top right",
                textfont=dict(color=col),
                name=name,
                legendgroup='low' if 'low' in fuel_blue else 'high',
                showlegend=False,
                mode='text',
                hoverinfo='skip',
            ))

            # hover template
            traces.append(go.Scatter(
                x=this_data.delta_ghgi * 1000,
                y=this_data.delta_cost,
                error_x=dict(
                    type='data',
                    array=this_data.delta_ghgi_uu * 1000,
                    arrayminus=this_data.delta_ghgi_ul * 1000,
                    thickness=0.0,
                ),
                error_y=dict(
                    type='data',
                    array=this_data.delta_cost_uu,
                    arrayminus=this_data.delta_cost_ul,
                    thickness=0.0,
                ),
                line_color=col,
                marker_size=0.000001,
                showlegend=False,
                mode='markers',
                customdata=this_data.year,
                hovertemplate=f"<b>{name}</b><br>Year: %{{customdata}}<br>"
                              f"Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                              f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}"
                              f"<extra></extra>",
            ))

            # error bars
            if self.cfg['show_errorbars']:
                this_data = this_data.query(f"year==[2025,2030,2040,2050]")
                traces.append(go.Scatter(
                    x=this_data.delta_ghgi * 1000,
                    y=this_data.delta_cost,
                    error_x=dict(
                        type='data',
                        array=this_data.delta_ghgi_uu * 1000,
                        arrayminus=this_data.delta_ghgi_ul * 1000,
                        thickness=self._styles['lw_thin'],
                    ),
                    error_y=dict(
                        type='data',
                        array=this_data.delta_cost_uu,
                        arrayminus=this_data.delta_cost_ul,
                        thickness=self._styles['lw_thin'],
                    ),
                    line_color=col,
                    marker_size=0.000001,
                    showlegend=False,
                    mode='markers',
                    hoverinfo='skip',
                ))

        return traces

    def _add_fscp_subplot_contours_top(self, fuel_specs: dict, blue_fuel: str, green_fuel: str, xmin: float,
                                       xmax: float, zmin: float, zmax: float, colourscale: list, linedensity: float,
                                       ymin: float, params_options: dict):
        traces = []

        # define data for plot grid
        leakage = np.linspace(xmin, xmax, self.cfg['plotting']['n_samples'])
        delta_cost = np.linspace(self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max'],
                                 self.cfg['plotting']['n_samples'])

        # calculate GHGI data from params
        gwp = fuel_specs[blue_fuel]['options']['gwp']
        gwp_other = _other_gwp(gwp)
        blue_options_other = fuel_specs[blue_fuel]['options'].copy()
        blue_options_other['gwp'] = gwp_other

        current_params_blue = fuel_specs[blue_fuel]['params'] \
            .query(f"year=={self.cfg['fuelYearTop']}") \
            .droplevel(level=1)
        current_params_green = fuel_specs[green_fuel]['params'] \
            .query(f"year=={self.cfg['fuelYearTop']}") \
            .droplevel(level=1)

        param_handler_blue = ParameterHandler(current_params_blue, params_options)
        param_handler_green = ParameterHandler(current_params_green, params_options)

        pars_blue = get_ghgi_params_blue(param_handler_blue, fuel_specs[blue_fuel]['options'])
        pars_green = get_ghgi_params_green(param_handler_green, fuel_specs[green_fuel]['options'])

        # calculate FSCPs for grid
        leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
        pars_blue['mlr'] = (leakage_v, 0, 0)
        ghgi_blue, ghgi_green = _get_ghgis(pars_blue, pars_green)
        fscp = delta_cost_v / (ghgi_blue - ghgi_green)

        # add contour traces
        traces.append(go.Heatmap(x=leakage * 100, y=delta_cost, z=fscp,
                                 zsmooth='best', showscale=False, hoverinfo='skip',
                                 zmin=zmin, zmax=zmax,
                                 colorscale=colourscale,
                                 colorbar=dict(
                                     x=1.0,
                                     y=0.5,
                                     len=1.0,
                                     titleside='top',
                                 )))

        traces.append(go.Contour(x=leakage * 100, y=delta_cost, z=fscp,
                                 showscale=False, contours_coloring='lines', hoverinfo='skip',
                                 colorscale=[
                                     [0.0, '#000000'],
                                     [1.0, '#000000'],
                                 ],
                                 line_width=self._styles['lw_ultrathin'],
                                 contours=dict(
                                     showlabels=True,
                                     start=zmin,
                                     end=zmax,
                                     size=linedensity,
                                 )))

        # determine other xaxes ranges
        range3 = [ghgi_blue[0][0], ghgi_blue[0][-1]]

        pars_blue = get_ghgi_params_blue(param_handler_blue, fuel_specs[blue_fuel]['options'])
        pars_blue_other = get_ghgi_params_blue(param_handler_blue, blue_options_other)
        ghgi_blue_base, _ = _get_ghgis(pars_blue, pars_green, base_only=True)
        ghgi_blue_other_base, _ = _get_ghgis(pars_blue_other, pars_green, base_only=True)

        range2 = [
            (x * pars_blue['mghgi'] + ghgi_blue_base - ghgi_blue_other_base) / pars_blue_other['mghgi']
            for x in [xmin, xmax]
        ]

        # add scatter traces
        x_vals = [pars_blue['mlr'][0] * 100, xmax * (pars_blue['mlr'][0] - range2[0]) / (range2[1] - range2[0]) * 100]
        y_val = (
            sum(e['val'] for e in calc_cost(param_handler_green, 'GREEN', fuel_specs[green_fuel]['options']).values())
            - sum(e['val'] for e in calc_cost(param_handler_blue, 'BLUE', fuel_specs[blue_fuel]['options']).values())
        )

        name = f"Comparing {fuel_specs[blue_fuel]['name']} with {fuel_specs[green_fuel]['name']}"
        col = self.cfg['fscp_colour'][blue_fuel.split('-')[-1] + '-' + green_fuel.split('-')[-1]]

        traces.append(go.Scatter(
            x=x_vals,
            y=[y_val] * 2,
            text=[f"{self.cfg['fuelYearTop']}, {gwp.upper()}" for gwp in [gwp, gwp_other]],
            textposition=['top right', 'top right'],
            textfont=dict(color=col),
            legendgroup=f"{blue_fuel}--{green_fuel}",
            showlegend=False,
            marker_size=self._styles['highlight_marker_sm'],
            line_color=col,
            mode='markers+text',
            customdata=[self.cfg['fuelYearTop'], ],
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>"
                          f"Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))

        annotations = []
        for i, gwpThis in enumerate([gwp, gwp_other]):
            x = x_vals[i]
            y = ymin - (4.0 if gwpThis == gwp else 8.0)

            annotations.append(go.layout.Annotation(
                x=x,
                y=y_val,
                ax=x,
                ay=y,
                text='{:.2f}'.format(x_vals[0]),
                arrowhead=0,
                arrowcolor=col,
                font_color=col,
                showarrow=True,
                arrowwidth=self._styles['lw_thin'],
            ))

        shapes = [go.layout.Shape(
            type='line',
            xref='x2',
            yref='y2',
            x0=xmax * 100,
            y0=y_val,
            x1=xmin * 100,
            y1=y_val,
            line_color=col,
            line_width=self._styles['lw_thin'],
        )]

        return traces, range2, range3, annotations, shapes

    def _add_fscp_subplot_contours_bottom(self, fuel_specs: dict, blue_fuel: str, green_fuel: str, xmin: float,
                                          xmax: float, zmin: float, zmax: float, colourscale: list, linedensity: float,
                                          params_options: dict):
        traces = []

        # define data for plot grid
        share = np.linspace(xmin, xmax, self.cfg['plotting']['n_samples'])
        delta_cost = np.linspace(self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max'],
                                 self.cfg['plotting']['n_samples'])

        # calculate GHGI data from params
        gwp = fuel_specs[blue_fuel]['options']['gwp']
        gwp_other = _other_gwp(gwp)
        green_options_other = fuel_specs[blue_fuel]['options'].copy()
        green_options_other['gwp'] = gwp_other

        current_params_blue = fuel_specs[blue_fuel]['params'] \
            .query(f"year=={self.cfg['fuelYearTop']}") \
            .droplevel(level=1)
        current_params_green = fuel_specs[green_fuel]['params'] \
            .query(f"year=={self.cfg['fuelYearTop']}") \
            .droplevel(level=1)

        param_handler_blue = ParameterHandler(current_params_blue, params_options)
        param_handler_green = ParameterHandler(current_params_green, params_options)

        pars_blue = get_ghgi_params_blue(param_handler_blue, fuel_specs[blue_fuel]['options'])
        pars_green = get_ghgi_params_green(param_handler_green, fuel_specs[green_fuel]['options'])

        # calculate FSCPs for grid
        share_v, delta_cost_v = np.meshgrid(share, delta_cost)
        pars_green['sh'] = (share_v, 0, 0)
        ghgi_blue, ghgi_green = _get_ghgis(pars_blue, pars_green)
        fscp = delta_cost_v / (ghgi_blue - ghgi_green)

        # recolour the bit of the graph where emissions of green are higher than blue
        for x in range(len(share)):
            for y in range(len(delta_cost)):
                if ghgi_green[x, y] > ghgi_blue:
                    fscp[x, y] = zmax + 10.0

        # add contour traces
        traces.append(go.Heatmap(x=share * 100, y=delta_cost, z=fscp,
                                 zsmooth='best', showscale=False, hoverinfo='skip',
                                 zmin=zmin, zmax=zmax,
                                 colorscale=colourscale,
                                 colorbar=dict(
                                     x=1.0,
                                     y=0.5,
                                     len=1.0,
                                     titleside='top',
                                 )))

        traces.append(go.Contour(x=share * 100, y=delta_cost, z=fscp,
                                 showscale=False, contours_coloring='lines', hoverinfo='skip',
                                 colorscale=[
                                     [0.0, '#000000'],
                                     [1.0, '#000000'],
                                 ],
                                 line_width=self._styles['lw_ultrathin'],
                                 contours=dict(
                                     showlabels=True,
                                     start=zmin,
                                     end=zmax,
                                     size=linedensity,
                                 )))

        # determine other xaxes ranges
        range3 = [ghgi_green[0][0], ghgi_green[0][-1]]

        pars_green = get_ghgi_params_green(param_handler_green, fuel_specs[green_fuel]['options'])
        pars_green_other = get_ghgi_params_green(param_handler_green, green_options_other)
        ghgi_green_base, _ = _get_ghgis(pars_blue, pars_green, base_only=True)
        ghgi_green_other_base, _ = _get_ghgis(pars_blue, pars_green_other, base_only=True)

        range2 = [
            (ghgi_green_base - ghgi_green_other_base + pars_green['eff'] * (pars_green['elfos'][0] -
             pars_green_other['elfos'][0]) + pars_green['eff'] * sh * (pars_green['elre'][0] -
             pars_green['elfos'][0])) / (pars_green_other['eff'] * (pars_green_other['elre'][0] -
             pars_green_other['elfos'][0]))
            for sh in [xmin, xmax]
        ]

        # add scatter traces
        x_val = pars_green['sh'] * 100
        y_val = (
            sum(e['val'] for e in calc_cost(param_handler_green, 'GREEN', fuel_specs[green_fuel]['options']).values())
            - sum(e['val'] for e in calc_cost(param_handler_blue, 'BLUE', fuel_specs[blue_fuel]['options']).values())
        )

        name = f"Comparing {fuel_specs[blue_fuel]['name']} with {fuel_specs[green_fuel]['name']}"
        col = self.cfg['fscp_colour'][blue_fuel.split('-')[-1] + '-' + green_fuel.split('-')[-1]]

        traces.append(go.Scatter(
            x=[x_val, ],
            y=[y_val],
            text=[self.cfg['fuelYearBottom'], ],
            textposition=["bottom right", "top right"],
            textfont=dict(color=col),
            legendgroup=f"{blue_fuel}--{green_fuel}",
            showlegend=False,
            marker_size=self._styles['highlight_marker_sm'],
            line_color=col,
            mode='markers+text',
            customdata=[self.cfg['fuelYearBottom'], ],
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>"
                          f"Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))

        return traces, range2, range3

    def _get_xaxis_styles(self, calced_ranges: dict):
        vspace = self.cfg['vertical_spacing']

        # settings for x axes 1 to 15 (6 and 11 are undefined)
        axis_settings = [
            (True, 1000, 'bottom', 'y', None, None, None),
            (True, 100, 'bottom', 'y2', None, None, 37.0),
            (True, 100, 'bottom', 'y3', None, None, 37.0),
            (True, 100, 'bottom', 'y4', None, None, None),
            (True, 100, 'bottom', 'y5', None, None, None),
            (False, None, None, None, None, None, None),
            (True, 100, 'bottom', 'free', 'x2', 0.5 + vspace / 2, None),
            (True, 100, 'bottom', 'free', 'x3', 0.5 + vspace / 2, None),
            (True, 100, 'bottom', 'free', 'x4', 0.0, None),
            (True, 100, 'bottom', 'free', 'x5', 0.0, None),
            (False, None, None, None, None, None, None),
            (True, 1000, 'top', 'free', 'x2', 1.0, None),
            (True, 1000, 'top', 'free', 'x3', 1.0, None),
            (True, 1000, 'top', 'free', 'x4', 0.5 - vspace / 2, 0.0),
            (True, 1000, 'top', 'free', 'x5', 0.5 - vspace / 2, 0.0),
        ]

        new_axes = {}
        for i, settings in enumerate(axis_settings):
            add, factor, side, anchor, overlay, position, standoff = settings

            if not add:
                continue

            axis_name = f"xaxis{i + 1}"

            if axis_name in calced_ranges:
                ran = [r * factor for r in calced_ranges[axis_name]]
            else:
                ran = [self.cfg['plotting'][f"{axis_name}_min"] * factor,
                       self.cfg['plotting'][f"{axis_name}_max"] * factor]

            title = self.cfg['labels'][axis_name]
            if i in [6, 7]:
                title = 38 * '&#160;' + title

            new_axes[axis_name] = dict(
                title=title,
                range=ran,
                side=side,
                anchor=anchor,
            )

            if overlay is not None:
                new_axes[axis_name]['overlaying'] = overlay

            if position is not None:
                new_axes[axis_name]['position'] = position

            if standoff is not None:
                new_axes[axis_name]['title'] = dict(text=title, standoff=standoff)

        new_axes['xaxis2']['dtick'] = 1.0
        new_axes['xaxis3']['dtick'] = 1.0

        new_axes['xaxis7']['ticklen'] = 25.0
        new_axes['xaxis7']['tick0'] = 0.0
        new_axes['xaxis7']['dtick'] = 0.5

        new_axes['xaxis8']['ticklen'] = 25.0
        new_axes['xaxis8']['tick0'] = 0.0
        new_axes['xaxis8']['dtick'] = 0.5

        new_axes['xaxis9']['ticklen'] = 25.0
        new_axes['xaxis10']['ticklen'] = 25.0

        return new_axes

    def _get_colour_scale(self):
        zmin = self.cfg['colourscale']['FSCPmin']
        zmax = self.cfg['colourscale']['FSCPmax']
        zran = self.cfg['colourscale']['FSCPmax'] - self.cfg['colourscale']['FSCPmin']
        csm = self.cfg['colourscale']['FSCPmid'] / zran

        colourscale = [
            [0.0, self.cfg['colours']['heatmap_low']],
            [csm, self.cfg['colours']['heatmap_medium']],
            [1.0, self.cfg['colours']['heatmap_high']],
        ]

        return zmin, zmax, colourscale


def _convert_fuel_data(fuel_data: pd.DataFrame, fuel_x: str, fuel_y: str):
    fuel_data = fuel_data[['fuel', 'type', 'year', 'cost', 'cost_uu', 'cost_ul', 'ghgi', 'ghgi_uu', 'ghgi_ul']]

    tmp = fuel_data.merge(fuel_data, how='cross', suffixes=('_x', '_y')). \
        query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y"). \
        dropna()

    tmp['year'] = tmp['year_x']

    tmp['delta_cost'] = tmp['cost_y'] - tmp['cost_x']
    tmp['delta_cost_uu'] = tmp['cost_uu_y'] + tmp['cost_ul_x']
    tmp['delta_cost_ul'] = tmp['cost_ul_y'] + tmp['cost_uu_x']

    tmp['delta_ghgi'] = tmp['ghgi_x'] - tmp['ghgi_y']
    tmp['delta_ghgi_uu'] = tmp['ghgi_uu_x'] + tmp['ghgi_ul_y']
    tmp['delta_ghgi_ul'] = tmp['ghgi_ul_x'] + tmp['ghgi_uu_y']

    fscp_data = tmp[['fuel_x', 'delta_cost', 'delta_cost_uu', 'delta_cost_ul',
                     'delta_ghgi', 'delta_ghgi_uu', 'delta_ghgi_ul', 'year']]

    return fscp_data


def _get_ghgis(pars_blue, pars_green, base_only: bool = False) -> tuple[float, float]:
    ghgi_blue = get_ghgi_blue(**pars_blue)
    ghgi_green = get_ghgi_green(**pars_green)

    return (sum(ghgi_blue[comp]['val'] for comp in ghgi_blue if not base_only or comp != 'scch4'),
            sum(ghgi_green[comp]['val'] for comp in ghgi_green if not base_only or comp != 'elec'))


def _get_cost_diff(pars_blue, pars_green):
    cost_blue = get_cost_blue(**pars_blue)
    cost_green = get_cost_green(**pars_green)

    return sum(cost_blue[comp]['val'] for comp in cost_green) - sum(cost_blue[comp]['val'] for comp in cost_blue)


def _other_gwp(gwp: str):
    return 'gwp20' if gwp == 'gwp100' else 'gwp100'
