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
            for sub, type in [('A', 'left'), ('B', 'right')]:
                subfigName = f"fig4{sub}" if application == 'heating' else f"figS4{sub}"

                # check if plotting is needed
                if subfigName not in subfig_names:
                    ret.update({subfigName: None})
                    continue

                # select data
                plotData, refData = self.__selectPlotData(outputs['fuelData'],
                                                     self.cfg['refFuel'][type], self.cfg['refYear'][type],
                                                     self.cfg['showFuels'][type], self.cfg['showYears'])

                # throw away all components
                plotData = plotData.drop(
                    columns=plotData.filter(regex=r"^(cost|ghgi)(_uu|_ul)?__.*$").columns.to_list(),
                    axis=1,
                )
                refData = refData.drop(
                    index=refData.filter(regex=r"^(cost|ghgi)(_uu|_ul)?__.*$").keys().to_list()
                )

                # add steel data for fig S4
                if application == 'steel':
                    steel = self.cfg['steelAssumptions']

                    for t in [f"{comp}_{unc}" for comp in ['cost', 'ghgi'] for unc in ['uu', 'ul']]:
                        plotData[t] *= steel['idreaf_demand_h2']
                    plotData['cost'] += steel['idreaf_cost']

                    refData['cost'] = steel['bfbof_cost']
                    refData['ghgi'] = steel['bfbof_ghgi']

                # define plotly figure
                fig = go.Figure()

                # produce figures
                fig = self.__produceFigure(fig, plotData, refData, outputs['fuelSpecs'], type, application)

                ret.update({subfigName: fig})

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def __selectPlotData(self, fuelsData: pd.DataFrame, refFuel: str, refYear: int, showFuels: list, showYears: list):
        plotData = fuelsData.query('fuel in @showFuels and year in @showYears')
        refData = fuelsData.query(f"fuel=='{refFuel}' & year=={refYear}").iloc[0]


        return plotData, refData


    def __produceFigure(self, fig: go.Figure, plotData: pd.DataFrame, refData: pd.Series, fuelSpecs: dict, type: str,
                        application: str):
        config = self.cfg

        # apply scaling
        if application=='heating':
            config = copy.deepcopy(config)
            plotData = plotData.copy()
            refData = refData.copy()

            config['plotting'][application]['ghgi_max'] *= 1000.0
            plotData[['ghgi', 'ghgi_uu', 'ghgi_ul']] *= 1000.0
            refData[['ghgi', 'ghgi_uu', 'ghgi_ul']] *= 1000.0


        # configure FSCP plotting
        FSCPConf = {
            'ghgi_min': 0.0,
            'ghgi_max': config['plotting'][application]['ghgi_max'],
            'cost_min': 0.0,
            'cost_max': config['plotting'][application]['cost_max'],
            'fscp_scaling': 1000.0 if application=='heating' else 1.0,
            'zmax': config['plotting'][application]['zmax'],
            'zdticks': config['plotting'][application]['zdticks'],
            'zdeltalines': config['plotting'][application]['zdeltalines'],
            'n_samples': config['plotting']['n_samples'],
            'colorbarTitle': '<i>FSCP</i><sub>NG→H<sub>2</sub></sub>' if application=='heating' else '<i>FSCP</i><sub>BF-BOF→H<sub>2</sub>-DR</sub>'
        }


        # add line traces
        traces = self.__addLineTraces(plotData, fuelSpecs, config)
        for trace in traces:
            fig.add_trace(trace)


        # add FSCP traces
        traces = self.__addFSCPTraces(refData, config['thickLines'][application][type], FSCPConf, self._styles['lw_thin'], self._styles['lw_ultrathin'], type == 'right')
        for trace in traces:
            fig.add_trace(trace)


        # determine y-axis plot range
        shift = 0.1
        ylow = 0.0 if application=='heating' else refData.cost - shift * (config['plotting']['steel']['cost_max'] - refData.cost)


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
        annotationStylingA = dict(xanchor='center', yanchor='bottom', showarrow=False,
                                  bordercolor='black', borderwidth=2, borderpad=3, bgcolor='white')

        topLabel = config['annotationLabels'][type]
        fig.add_annotation(
            x=0.50,
            xref='x domain',
            y=1.0,
            yref='y domain',
            yshift=20.0,
            text=topLabel,
            **annotationStylingA,
        )

        annotationStylingB = dict(xanchor='left', yanchor='top', showarrow=False)
        fig.add_annotation(
            x=0.01*config['plotting'][application]['ghgi_max'],
            y=refData.cost,
            xref='x', yref='y', text=config['baselineLabels'][application],
            **annotationStylingB,
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


    def __addLineTraces(self, plotData: pd.DataFrame, fuelSpecs: dict, config: dict):
        traces = []
        hasLegend = []

        for fuel in plotData.fuel.unique():
            # line properties
            descs = [
                'progressive' if 'prog' in fuel else 'conservative',
                'low supply-chain CO<sub>2</sub>' if fuel.endswith('lowscco2') else None,
            ]
            name = fuelSpecs[fuel]['name'].split(' (')[0] + f" ({', '.join([d for d in descs if d])})"
            col = fuelSpecs[fuel]['colour']
            tech = fuel
            dashed = any(t in fuel for t in config['tokensDashed'])


            # data
            thisData = plotData.query(f"fuel=='{fuel}'")


            # points and lines
            traces.append(go.Scatter(
                x=thisData.ghgi,
                y=thisData.cost,
                text=thisData.year if not fuel.endswith('lowscco2') else None,
                textposition='top left' if 'pess' in fuel else 'bottom right',
                textfont=dict(color=col),
                name=name,
                legendgroup=fuel,
                showlegend=False,
                mode='markers+text',# if tech not in hasLegend else 'markers',
                line=dict(color=col),
                marker_size=self._styles['highlight_marker_sm'],
                hoverinfo='skip',
            ))

            traces.append(go.Scatter(
                x=thisData.ghgi,
                y=thisData.cost,
                name=name,
                legendgroup=tech,
                showlegend=tech not in hasLegend,
                line=dict(color=col, width=self._styles['lw_default'], dash='dot' if dashed else 'solid'),
                mode='lines',
                hoverinfo='skip',
            ))

            if tech not in hasLegend:
                hasLegend.append(tech)


            # hover template
            traces.append(go.Scatter(
                x=thisData.ghgi,
                y=thisData.cost,
                error_x=dict(type='data', array=thisData.ghgi_uu, arrayminus=thisData.ghgi_ul, thickness=0.0),
                error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=0.0),
                line_color=col,
                showlegend=False,
                mode='lines',
                line_width=0.000001,
                customdata=thisData.year,
                hovertemplate=f"<b>{name}</b><br>Year: %{{customdata}}<br>Carbon intensity: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>Direct cost: %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
            ))


            # error bars
            thisData = thisData.query(f"year==[2025,2030,2040,2050]")
            traces.append(go.Scatter(
                x=thisData.ghgi,
                y=thisData.cost,
                error_x=dict(type='data', array=thisData.ghgi_uu, arrayminus=thisData.ghgi_ul, thickness=self._styles['lw_thin']),
                error_y=dict(type='data', array=thisData.cost_uu, arrayminus=thisData.cost_ul, thickness=self._styles['lw_thin']),
                line_color=col,
                marker_size=0.000001,
                showlegend=False,
                mode='markers',
                customdata=thisData.year,
                hoverinfo='skip',
            ))


        return traces


    def __addFSCPTraces(self, refData: pd.Series, thickLines: list, FSCPConf: dict, lw_thin: float, lw_ultrathin: float, showscale: bool):
        traces = []

        ghgi_samples = np.linspace(FSCPConf['ghgi_min'], FSCPConf['ghgi_max'], FSCPConf['n_samples'])
        cost_samples = np.linspace(FSCPConf['cost_min'], FSCPConf['cost_max'], FSCPConf['n_samples'])
        ghgi_v, cost_v = np.meshgrid(ghgi_samples, cost_samples)

        ghgi_ref = refData.ghgi
        cost_ref = refData.cost

        fscp = (cost_v - cost_ref)/(ghgi_ref - ghgi_v) * FSCPConf['fscp_scaling']

        # heatmap
        tickvals = [FSCPConf['zdticks']*i for i in range(int(FSCPConf['zmax']/FSCPConf['zdticks'])+1)]
        ticktext = [str(v) for v in tickvals]
        ticktext[0] = f"≤ {ticktext[0]}"
        ticktext[-1] = f"≥ {ticktext[-1]}"
        traces.append(go.Heatmap(
            x=ghgi_samples, y=cost_samples, z=fscp,
            zsmooth='best', hoverinfo='skip',
            zmin=0.0, zmax=FSCPConf['zmax'],
            colorscale=[
                [0.0, '#c6dbef'],
                [1.0, '#f7bba1'],
            ],
            colorbar=dict(
                x=1.05,
                y=0.25,
                len=0.5,
                title=FSCPConf['colorbarTitle'],
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
                                     size=FSCPConf['zdeltalines'],
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
        for kwargs in thickLines:
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
