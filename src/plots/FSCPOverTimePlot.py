import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
from plotly.subplots import make_subplots

from src.proc_func.fscps import calc_fscps
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class FSCPOverTimePlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('FSCPOverTimePlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        if 'fig3' not in subfig_names and 'figS2' not in subfig_names:
            return {}
        ret = {}

        # select which lines to plot based on function argument
        plot_scatter, plot_lines = self._select_plot_fscps(
            outputs['fuelData'], self.cfg['selected_cases'], calc_unc=('figS2' in subfig_names),
        )

        # get carbon price trajectory data
        cp_traj_data = self._compute_cp_traj()

        # produce figure 3
        ret['fig3'] = (
            self._produce_figure(plot_scatter, plot_lines, outputs['fuelSpecs'], cp_traj_data)
            if 'fig3' in subfig_names else None
        )

        # produce figure S2
        ret['figS2'] = (
            self._produce_figure(plot_scatter, plot_lines, outputs['fuelSpecs'], cp_traj_data, is_uncertainty=True)
            if 'figS2' in subfig_names else None
        )

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _select_plot_fscps(self, fuel_data: pd.DataFrame, selected_cases: dict,
                           calc_unc: bool = True) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
        plot_scatter = {}
        plot_interpolation = {}

        for scid, fuels in selected_cases.items():
            # insert interpolation points
            t = np.linspace(fuel_data['year'].min(), fuel_data['year'].max(), self.cfg['n_samples'])

            tmp = []
            for f in fuels:
                support = fuel_data \
                    .query(f"fuel=='{f}'") \
                    .reset_index(drop=True) \
                    .astype({'year': float})

                interpolation = dict(
                    year=t,
                    fuel=self.cfg['n_samples'] * [f],
                    type=self.cfg['n_samples'] * [support.type.iloc[0]],
                )

                tmp.append(
                    pd.merge(
                        support,
                        pd.DataFrame(interpolation, columns=support.keys()),
                        on=['year', 'fuel', 'type'],
                        how='outer',
                        suffixes=('', '_drop'),
                    )
                    .sort_values(by=['year'])
                    .reset_index(drop=True)
                    .interpolate()
                    .dropna(axis='columns')
                )

            fuel_data_interpolated = pd.concat(tmp)

            # compute FSCPs
            plot_interpolation[scid] = calc_fscps(fuel_data_interpolated, calc_unc).assign(
                tid=lambda r: r.fuel_y + ' to ' + r.fuel_x)
            years = fuel_data.year.unique()
            plot_scatter[scid] = plot_interpolation[scid].query(f"year in @years")

        return plot_scatter, plot_interpolation

    def _produce_figure(self, plot_scatter: dict, plot_lines: dict, fuel_specs: dict, cp_traj_data: pd.DataFrame,
                        is_uncertainty: bool = False):
        # plot
        fig = make_subplots(
            rows=2,
            cols=2,
            shared_yaxes=True,
            horizontal_spacing=0.025,
            vertical_spacing=0.1,
        )

        # list of subfigs including row and col count for easy access
        subfigs = [(k // 2 + 1, k % 2 + 1, scid) for k, scid in enumerate(self.cfg['selected_cases'])]

        # whether to show the box with a legend explaining the cricle annotations
        show_annotation_legend = self._target != 'webapp' and not is_uncertainty

        # add FSCP traces
        has_legend = []
        for i, j, scid in subfigs:
            all_traces = self._add_fscp_traces(plot_scatter[scid], plot_lines[scid], fuel_specs,
                                               uncertainity=is_uncertainty)
            for tid, traces in all_traces.items():
                if is_uncertainty and (not self.cfg['bgfscp_unc'] and 'NG' not in tid):
                    continue
                tid_techs = '-'.join([fuel.split('-')[0] + '-' + fuel.split('-')[-1] for fuel in tid.split(' to ')])
                if all(fuel in self.cfg['selected_cases'][scid] for fuel in tid.split(' to ')):
                    for trace in traces:
                        if tid_techs in has_legend:
                            trace.showlegend = False
                        fig.add_trace(trace, row=i, col=j)
                    if tid_techs not in has_legend:
                        has_legend.append(tid_techs)

        # compute and plot carbon price trajectory
        if not is_uncertainty or self.cfg['show_cp_unc']:
            traces = self._add_cp_traces(cp_traj_data)
            for trace in traces:
                for i, j, scid in subfigs:
                    if i > 1 or j > 1:
                        trace.showlegend = False
                    fig.add_trace(trace, row=i, col=j)

        # zero y line
        for i, j, _ in subfigs:
            fig.add_hline(0.0, line_width=self._styles['lw_thin'], line_color='black', row=i, col=j)

        # add circles on intersects
        if not is_uncertainty:
            self._add_annotations(fig, cp_traj_data, fuel_specs, plot_lines)

        # add top and left annotation
        annotation_styling = dict(
            xanchor='center', yanchor='middle', showarrow=False,
            bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white'
        )

        for i in range(2):
            fig.add_annotation(
                x=0.50,
                xref=f"x{str(i + 1) if i else ''} domain",
                y=1.0,
                yref='y domain',
                yshift=40,
                text=self.cfg['sidelabels']['top'][i],
                **annotation_styling
            )

            fig.add_annotation(
                x=0.0,
                xref='x domain',
                xshift=-150.0 if self._target != 'webapp' else -100.0,
                y=0.5,
                yref=f"y{str(i + 2) if i else ''} domain",
                text=self.cfg['sidelabels']['left'][i],
                textangle=-90,
                **annotation_styling
            )

        # update axes titles and ranges
        fig.update_layout(
            **{f"xaxis{i + 1 if i else ''}": dict(
                title=self.cfg['labels']['time'],
                range=[self.cfg['plotting']['t_min'], self.cfg['plotting']['t_max']],
            ) for i in range(4)},
            **{f"yaxis{i + 1 if i else ''}": dict(
                title=self.cfg['labels']['fscp'] if (i + 1) % 2 else '',
                range=[self.cfg['plotting']['fscp_min'], self.cfg['plotting']['fscp_max']],
            ) for i in range(4)},
            margin_l=180.0,
        )

        # set legend position
        fig.update_layout(
            legend=dict(
                orientation='h',
                xanchor='left',
                x=0.0,
                yanchor='top',
                y=self.cfg['spacings']['legendPosY'] if show_annotation_legend else -0.1,
            ),
        )

        # add legend for annotations
        if show_annotation_legend:
            self._add_annotations_legend(fig)

            fig.update_layout(
                **{f"yaxis{i + 1 if i else ''}": dict(
                    domain=[
                        1.0 - self.cfg['spacings']['yShareTop'] if i >= 2 else 1.0 - (
                                    self.cfg['spacings']['yShareTop'] - self.cfg['spacings']['spacingTop']) / 2,
                        1.0 - (self.cfg['spacings']['yShareTop'] - self.cfg['spacings']['spacingTop']) / 2 -
                        self.cfg['spacings']['spacingTop'] if i >= 2 else 1.0,
                    ],
                ) for i in range(4)},
                xaxis5=dict(
                    range=[0, 1],
                    domain=[0.0, self.cfg['spacings']['annotationsLegendWidth']],
                    anchor='y5',
                    showticklabels=False,
                    ticks='',
                ),
                yaxis5=dict(
                    range=[0, 1],
                    domain=[0.0, self.cfg['spacings']['annotationsLegendHeight']],
                    anchor='x5',
                    showticklabels=False,
                    ticks='',
                ),
            )

        return fig

    # add FSCP traces
    def _add_fscp_traces(self, plot_scatter: pd.DataFrame, plot_lines: pd.DataFrame, fuel_specs: dict,
                         uncertainity: bool = False) -> dict:
        traces = {}

        for tid in plot_scatter.tid.unique():
            this_traces = []

            this_scatter = plot_scatter.query(f"tid=='{tid}'").reset_index(drop=True)
            this_line = plot_lines.query(f"tid=='{tid}'").reset_index(drop=True)

            # line properties
            fuel_x = this_scatter.fuel_x.iloc[0]
            fuel_y = this_scatter.fuel_y.iloc[0]
            name_x = fuel_specs[fuel_x]['shortname']
            name_y = 'NG' if fuel_y.startswith('NG') else fuel_specs[fuel_y]['shortname']
            name_case = 'progressive' if fuel_x.endswith('prog') else 'conservative'
            name = f"{name_y}→{name_x} ({name_case})"
            col = (self.cfg['fscp_colour'][fuel_y.split('-')[-1] + '-' + fuel_x.split('-')[-1]]
                   if 'NG' not in tid else
                   fuel_specs[fuel_x]['colour'])
            isbluegreen = 'NG' not in fuel_y

            if isbluegreen and this_line.fscp.max() > 2000.0:
                y = this_line.loc[this_line.fscp.idxmax(), 'year']
                q = f"year>={y}"
                this_line = this_line.query(q)
                this_scatter = this_scatter.query(q)

            # scatter plot
            this_traces.append(go.Scatter(
                x=this_scatter['year'],
                y=this_scatter['fscp'],
                name=name,
                legendgroup=0 if isbluegreen else 1,
                showlegend=False,
                mode='markers',
                line=dict(color=col, width=self._styles['lw_default']),
                marker=dict(symbol='x-thin', size=self._styles['highlight_marker_sm'],
                            line={'width': self._styles['lw_thin'], 'color': col}, ),
                hoverinfo='skip',
            ))

            # line plot
            this_traces.append(go.Scatter(
                x=this_line['year'],
                y=this_line['fscp'],
                legendgroup=0 if isbluegreen else 1,
                legendgrouptitle=dict(
                    text=f"<b>{self.cfg['legendlabels'][1]}:</b>"
                         if isbluegreen else
                         f"<b>{self.cfg['legendlabels'][0]}:</b>",
                ),
                name=name,
                mode='lines',
                line=dict(
                    color=col,
                    width=self._styles['lw_default'],
                    dash='dot'
                         if fuel_x in self.cfg['cases_dashed'] or fuel_y in self.cfg['cases_dashed'] else
                         'solid'
                ),
                hovertemplate=f"<b>{name}</b><br>Year: %{{x:d}}<br>"
                              f"FSCP: %{{y:.2f}}"
                              f"<extra></extra>",
            ))

            # uncertainity envelope
            if uncertainity:
                x = np.concatenate((this_line['year'], this_line['year'][::-1]))
                y = np.concatenate(
                    (this_line['fscp'] + this_line['fscp_uu'], (this_line['fscp'] - this_line['fscp_ul'])[::-1]))

                this_traces.append(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(col), .2)),
                    fill='toself',
                    line=dict(
                        width=self._styles['lw_ultrathin'],
                        color=col,
                    ),
                    showlegend=False,
                    hoverinfo="none",
                ))

            traces[tid] = this_traces

        return traces

    # add annotations explaining intersections of lines with markers
    def _add_annotations(self, fig: go.Figure, cp_traj_data: pd.DataFrame, fuel_specs: dict,
                         plot_lines: dict[str, pd.DataFrame]):
        for i, j, scid in [(k // 2 + 1, k % 2 + 1, scid) for k, scid in enumerate(self.cfg['selected_cases'])]:
            points = self._calc_points(cp_traj_data, plot_lines[scid], fuel_specs, self.cfg['selected_cases'][scid])
            data = points.query(f"delta < 5.0")

            for _, row in data.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=[row.year],
                        y=[row.fscp],
                        text=[int(row.label)],
                        mode='markers+text',
                        marker=dict(symbol='circle-open', size=self._styles['highlight_marker'],
                                    line={'width': self._styles['lw_thin']}, color=row.colour),
                        textfont_color=row.colour,
                        textposition='bottom center',
                        showlegend=False,
                        hovertemplate=f"<b>Milestone {int(row.label)}:</b> "
                                      f"{self.cfg['annotationTexts'][f'point{int(row.label)}']}"
                                      f"<br>Time: %{{x:.2f}}<br>FSCP: %{{y:.2f}}"
                                      f"<extra></extra>",
                    ),
                    row=i,
                    col=j,
                )

    # compute where annotations should be added
    def _calc_points(self, cp_traj_data: pd.DataFrame, plot_lines: pd.DataFrame, fuel_specs: dict,
                     fuels: list) -> pd.DataFrame:
        points = []

        types = ['NG', 'BLUE', 'GREEN']
        grouped_fuels = {t: [f for f in fuels if not plot_lines.query(
            f"(fuel_x=='{f}' and type_x=='{t}') or (fuel_y=='{f}' and type_y=='{t}')").empty] for t in types}

        for fuel_ref, fuel_blue, fuel_green in [(r, b, g)
                                                for r in grouped_fuels['NG']
                                                for b in grouped_fuels['BLUE']
                                                for g in grouped_fuels['GREEN']]:
            drop_cols = ['tid', 'type_x', 'type_y', 'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']
            green_line = plot_lines \
                .query(f"fuel_y=='{fuel_ref}' & fuel_x=='{fuel_green}'") \
                .drop(columns=drop_cols) \
                .reset_index(drop=True)
            blue_line = plot_lines \
                .query(f"fuel_y=='{fuel_ref}' & fuel_x=='{fuel_blue}'") \
                .drop(columns=drop_cols) \
                .reset_index(drop=True)
            red_line = plot_lines \
                .query(f"fuel_y=='{fuel_blue}' & fuel_x=='{fuel_green}'") \
                .drop(columns=drop_cols) \
                .reset_index(drop=True)

            purple_line = cp_traj_data.drop(columns=['name', 'CP_u', 'CP_l'])

            # marker 4
            diff_lines = pd.merge(blue_line, green_line, on=['year'], suffixes=('', '_right'))
            diff_lines['delta'] = (diff_lines['fscp'] - diff_lines['fscp_right']).abs()
            points.append(
                diff_lines
                .nsmallest(1, 'delta')
                .drop(columns=['fscp_right'])
                .head(1)
                .assign(label=4, colour='black')
            )

            if fuel_green in self.cfg['cases_dashed'] or fuel_blue in self.cfg['cases_dashed']:
                continue

            # markers 1-3
            for i, line in enumerate([blue_line, green_line, red_line]):
                fuel_x = line.fuel_x.iloc[0]
                fuel_y = line.fuel_y.iloc[0]
                col = (self.cfg['fscp_colour'][fuel_y.split('-')[-1] + '-' + fuel_x.split('-')[-1]]
                       if 'NG' not in fuel_y else
                       fuel_specs[fuel_x]['colour'])
                diff_lines = pd.merge(line, purple_line, on=['year'])
                diff_lines['delta'] = (diff_lines['fscp'] - diff_lines['CP']).abs()
                points.append(
                    diff_lines.nsmallest(1, 'delta').drop(columns=['CP']).head(1).assign(label=i + 1, colour=col))

            # marker 5
            red_line['abs'] = red_line['fscp'].abs()
            points.append(
                red_line.nsmallest(1, 'abs').assign(delta=lambda r: r.fscp).head(1).assign(label=5, colour='black'))

        return pd.concat(points)

    # plot legend for annotations explaining intersections of lines with markers
    def _add_annotations_legend(self, fig: go.Figure):
        xmargin = 0.01
        ymargin = 0.05
        lineheight = 0.2
        spacing = 0.02

        for i in range(2):
            t = self.cfg['annotationTexts'][f"heading{i + 1}"]
            fig.add_annotation(
                text=f"<b>{t}:</b>",
                align='left',
                xanchor='left',
                x=xmargin,
                yanchor='top',
                y=(0.5 if i else 1.0) - ymargin,
                xref='x5 domain',
                yref='y5 domain',
                showarrow=False,
            )

        labels = [
            [
                i + 1,
                (i % 2 + (2 if i == 4 else 0)) * 0.33 * 1.13 + 2 * xmargin,
                (1.0 if i < 2 else 0.5) - ymargin - lineheight,
            ]
            for i in range(5)
        ]

        psi, psx, psy = zip(*labels)
        fig.add_trace(
            go.Scatter(
                x=psx,
                y=psy,
                text=psi,
                mode='markers+text',
                marker=dict(symbol='circle-open', size=self._styles['highlight_marker'],
                            line={'width': self._styles['lw_thin']}, color='black'),
                textposition='bottom center',
                showlegend=False,
                hoverinfo='skip',
                xaxis='x5',
                yaxis='y5',
            )
        )

        for i, x, y in labels:
            t = self.cfg['annotationTexts'][f"point{i}"]
            fig.add_annotation(
                text=f"{t}",
                align='left',
                xanchor='left',
                x=x + spacing,
                yanchor='top',
                y=y + 0.05,
                xref='x5 domain',
                yref='y5 domain',
                showarrow=False,
            )

    # compute carbon price trajectories
    def _compute_cp_traj(self) -> pd.DataFrame:
        years: list = self._glob_cfg['co2price_traj']['years']
        values: dict = self._glob_cfg['co2price_traj']['values']
        n_samples: int = self.cfg['n_samples']

        v_mean = []
        v_upper = []
        v_lower = []

        for i, year in enumerate(years):
            vals = [v[i] for v in values.values()]
            mean = sum(vals) / len(vals)
            v_mean.append(mean)
            v_upper.append(max(vals) - mean)
            v_lower.append(mean - min(vals))

        # create data frame with time and cp values
        cp_data = pd.DataFrame({
            'year': [float(y) for y in years],
            'CP': v_mean,
            'CP_u': v_upper,
            'CP_l': v_lower,
        })

        # interpolate in between
        samples = pd.DataFrame({'year': np.linspace(years[0], years[-1], n_samples)})
        dtypes = {'year': float, 'CP': float, 'CP_u': float, 'CP_l': float}
        cp_data = cp_data.merge(samples, how='outer').sort_values(by=['year']).astype(dtypes).interpolate()

        # add name to dataframe
        cp_data['name'] = 'cp'

        return cp_data

    # plot carbon-price traces
    def _add_cp_traces(self, cp_traj_data: pd.DataFrame) -> list:
        traces = []

        name = self.cfg['carbon_price_config']['name']
        colour = self.cfg['carbon_price_config']['colour']

        # add main graphs (FSCP and CP)
        traces.append(go.Scatter(
            name=name,
            legendgroup=3,
            legendgrouptitle=dict(text=f"<b>{self.cfg['legendlabels'][2]}</b>:"),
            mode='lines',
            x=cp_traj_data['year'],
            y=cp_traj_data['CP'],
            line_color=colour,
            line_width=self._styles['lw_thin'],
            showlegend=True,
            hovertemplate=f"<b>{name}</b><br>Time: %{{x:.2f}}<br>Carbon price: %{{y:.2f}}<extra></extra>",
        ))

        data_x = cp_traj_data['year']
        data_yu = cp_traj_data['CP'] + cp_traj_data['CP_u']
        data_yl = cp_traj_data['CP'] - cp_traj_data['CP_l']

        error_band = go.Scatter(
            name='Uncertainty Range',
            legendgroup=3,
            x=pd.concat([data_x, data_x[::-1]], ignore_index=True),
            y=pd.concat([data_yl, data_yu[::-1]], ignore_index=True),
            mode='lines',
            marker=dict(color=colour),
            fillcolor=("rgba({}, {}, {}, 0.1)".format(*hex_to_rgb(colour))),
            fill='toself',
            line=dict(width=self._styles['lw_ultrathin']),
            showlegend=False,
            hoverinfo='skip'
        )
        traces.append(error_band)

        return traces
