import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.fuels.calc_cost import getCostBlue, getCostGreen, calcCost
from src.data.fuels.calc_ghgi import getGHGIBlue, getGHGIGreen, getGHGIParamsGreen, getGHGIParamsBlue
from src.data.fuels.helper_funcs import ParameterHandler
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class BlueGreenPlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('BlueGreenPlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {}

        # produce figure S2
        ret['figS3'] = self._produceFigureFull(outputs['fuelSpecs'], outputs['fuelData'], inputs['params_options']) \
            if 'figS3' in subfig_names else None

        return self.add_gwp_label(inputs['options']['gwp'], ret)

    def _produceFigureFull(self, fuelSpecs: dict, fuelData: pd.DataFrame, params_options: dict):
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

        calcedRanges = {}

        # get colour scale config
        zmin, zmax, colourscale = self.__getColourScale()

        # add FSCP traces for main plot (part a)
        traces = self.__addFSCPContours(zmin, zmax, colourscale)
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[0])

        # add scatter curves for main plot (part a)
        traces = self.__addFSCPScatterCurves(fuelData)
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[0])

        # add FSCP traces in subplots
        xmin, xmax = self.cfg['plotting']['xaxis2_min'], self.cfg['plotting']['xaxis2_max']
        traces, calcedRanges['xaxis7'], calcedRanges['xaxis12'], annotationsTop, shapesTop = (
            self.__addFSCPSubplotContoursTop(
                fuelSpecs, self.cfg['fuelBlueLeft'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax,
                colourscale, self.cfg['linedensity']['plot2'], self.cfg['plotting']['yaxis2_min'], params_options)
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[1])
        for a in annotationsTop:
            a.update(dict(
                xref='x2',
                yref='y2',
                axref='x2',
                ayref='y2',
            ))
            fig.add_annotation(a, **rowcol_mapping[1])
        for s in shapesTop:
            s.update(dict(
                xref='x2',
                yref='y2',
            ))
            fig.add_shape(s, **rowcol_mapping[1])

        xmin, xmax = self.cfg['plotting']['xaxis3_min'], self.cfg['plotting']['xaxis3_max']
        traces, calcedRanges['xaxis8'], calcedRanges['xaxis13'], annotationsTop, shapesTop = (
            self.__addFSCPSubplotContoursTop(
                fuelSpecs, self.cfg['fuelBlueRight'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax,
                colourscale, self.cfg['linedensity']['plot3'], self.cfg['plotting']['yaxis2_min'], params_options)
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[2])
        for a in annotationsTop:
            a.update(dict(
                xref='x3',
                yref='y3',
                axref='x3',
                ayref='y3',
            ))
            fig.add_annotation(a, **rowcol_mapping[2])
        for s in shapesTop:
            s.update(dict(
                xref='x3',
                yref='y3',
            ))
            fig.add_shape(s, **rowcol_mapping[2])

        xmin, xmax = self.cfg['plotting']['xaxis4_min'], self.cfg['plotting']['xaxis4_max']
        traces, calcedRanges['xaxis9'], calcedRanges['xaxis14'] = self.__addFSCPSubplotContoursBottom(
            fuelSpecs, self.cfg['fuelBlueLeft'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax, colourscale,
            self.cfg['linedensity']['plot4'], params_options,
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[3])

        xmin, xmax = self.cfg['plotting']['xaxis5_min'], self.cfg['plotting']['xaxis5_max']
        traces, calcedRanges['xaxis10'], calcedRanges['xaxis15'] = self.__addFSCPSubplotContoursBottom(
            fuelSpecs, self.cfg['fuelBlueRight'], self.cfg['fuelGreen'], xmin, xmax, zmin, zmax, colourscale,
            self.cfg['linedensity']['plot5'], params_options,
        )
        for trace in traces:
            fig.add_trace(trace, **rowcol_mapping[4])

        # add white annotation labels
        annotationStyling = dict(x=0.01, y=0.985, xanchor='left', yanchor='top', showarrow=False, bordercolor='black',
                                 borderwidth=2, borderpad=3, bgcolor='white')
        for k, f in enumerate(['fuelBlueLeft', 'fuelBlueRight'] * 2):
            t = ('Conservative' if self.cfg[f].endswith('cons') else 'Progressive') + ' to ' + (
                'conservative' if self.cfg['fuelGreen'].endswith('cons') else 'progressive')
            fig.add_annotation(xref=f"x{k + 2} domain", yref=f"y{k + 2} domain", text=t, **annotationStyling)

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
        newAxes = self.__getXAxesStyle(calcedRanges)
        fig.update_layout(**newAxes)

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

    def __addFSCPContours(self, zmin: float, zmax: float, colourscale: list):
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

    def __addFSCPScatterCurves(self, fuelData: pd.DataFrame, colourfull=False):
        traces = []

        hasYearMarker = []
        colIndex = 0
        for fuelBlue, fuelGreen in [(fB, fG) for fB in self.cfg['fuelsScatterBlue'] for fG in self.cfg['fuelsScatterGreen']]:
            thisData = _convertFuelData(fuelData, fuelBlue, fuelGreen)

            name = ('Conservative' if 'cons' in fuelBlue else 'Progressive') + ' to ' + (
                'conservative' if 'cons' in fuelGreen else 'progressive')
            legendgrouptitle = 'Low gas price' if 'low' in fuelBlue else 'High gas price'
            # col = px.colors.qualitative.Plotly[colIndex] if colourfull else config['fscp_colour'][fuelBlue.split('-')[-1] + '-' + fuelBlue.split('-')[-1]]
            col = self.cfg['fscp_colour'][fuelBlue.split('-')[-1] + '-' + fuelGreen.split('-')[-1]]
            colIndex += 1

            # markers
            traces.append(go.Scatter(
                x=thisData.delta_ghgi * 1000,
                y=thisData.delta_cost,
                text=thisData.year,
                textposition="top right",
                textfont=dict(color=col),
                name=name,
                legendgroup='low' if 'low' in fuelBlue else 'high',
                legendgrouptitle=dict(text=f"<b>{legendgrouptitle}</b>"),
                showlegend=True,
                line=dict(color=col, width=self._styles['lw_default'], dash='dot' if 'low' in fuelBlue else None),
                mode='lines',
                hoverinfo='skip',
            ))

            # lines
            traces.append(go.Scatter(
                x=thisData.delta_ghgi * 1000,
                y=thisData.delta_cost,
                legendgroup='low' if 'low' in fuelBlue else 'high',
                showlegend=False,
                line=dict(color=col, width=self._styles['lw_default']),
                marker_size=self._styles['highlight_marker_sm'],
                mode='markers',
                hoverinfo='skip',
            ))

            # year text
            textData = thisData.query(f"year in {self.cfg['showYearNumbers']}")
            traces.append(go.Scatter(
                x=textData.delta_ghgi * 1000,
                y=textData.delta_cost,
                text=textData.year,
                textposition="top right",
                textfont=dict(color=col),
                name=name,
                legendgroup='low' if 'low' in fuelBlue else 'high',
                showlegend=False,
                mode='text',
                hoverinfo='skip',
            ))

            # hover template
            traces.append(go.Scatter(
                x=thisData.delta_ghgi * 1000,
                y=thisData.delta_cost,
                error_x=dict(type='data', array=thisData.delta_ghgi_uu * 1000, arrayminus=thisData.delta_ghgi_ul * 1000,
                             thickness=0.0),
                error_y=dict(type='data', array=thisData.delta_cost_uu, arrayminus=thisData.delta_cost_ul,
                             thickness=0.0),
                line_color=col,
                marker_size=0.000001,
                showlegend=False,
                mode='markers',
                customdata=thisData.year,
                hovertemplate=f"<b>{name}</b><br>Year: %{{customdata}}<br>Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                              f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
            ))

            # error bars
            if self.cfg['show_errorbars']:
                thisData = thisData.query(f"year==[2025,2030,2040,2050]")
                traces.append(go.Scatter(
                    x=thisData.delta_ghgi * 1000,
                    y=thisData.delta_cost,
                    error_x=dict(type='data', array=thisData.delta_ghgi_uu * 1000,
                                 arrayminus=thisData.delta_ghgi_ul * 1000, thickness=self._styles['lw_thin']),
                    error_y=dict(type='data', array=thisData.delta_cost_uu, arrayminus=thisData.delta_cost_ul,
                                 thickness=self._styles['lw_thin']),
                    line_color=col,
                    marker_size=0.000001,
                    showlegend=False,
                    mode='markers',
                    hoverinfo='skip',
                ))

        return traces

    def __addFSCPSubplotContoursTop(self, fuelSpecs: dict, blueFuel: str, greenFuel: str, xmin: float, xmax: float,
                                    zmin: float, zmax: float, colourscale: list, linedensity: float, ymin: float,
                                    params_options: dict):
        traces = []

        # define data for plot grid
        leakage = np.linspace(xmin, xmax, self.cfg['plotting']['n_samples'])
        delta_cost = np.linspace(self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max'],
                                 self.cfg['plotting']['n_samples'])

        # calculate GHGI data from params
        gwp = fuelSpecs[blueFuel]['options']['gwp']
        gwpOther = _otherGwp(gwp)
        blueOptionsOther = fuelSpecs[blueFuel]['options'].copy()
        blueOptionsOther['gwp'] = gwpOther

        currentParamsBlue = fuelSpecs[blueFuel]['params'].query(f"year=={self.cfg['fuelYearTop']}").droplevel(level=1)
        currentParamsGreen = fuelSpecs[greenFuel]['params'].query(f"year=={self.cfg['fuelYearTop']}").droplevel(level=1)

        paramHandlerBlue = ParameterHandler(currentParamsBlue, params_options)
        paramHandlerGreen = ParameterHandler(currentParamsGreen, params_options)

        pBlue = getGHGIParamsBlue(paramHandlerBlue, fuelSpecs[blueFuel]['options'])
        pGreen = getGHGIParamsGreen(paramHandlerGreen, fuelSpecs[greenFuel]['options'])

        # calculate FSCPs for grid
        leakage_v, delta_cost_v = np.meshgrid(leakage, delta_cost)
        pBlue['mlr'] = (leakage_v, 0, 0)
        GHGIBlue, GHGIGreen = _getGHGIs(pBlue, pGreen)
        fscp = delta_cost_v / (GHGIBlue - GHGIGreen)

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
        range3 = [GHGIBlue[0][0], GHGIBlue[0][-1]]

        pBlue = getGHGIParamsBlue(paramHandlerBlue, fuelSpecs[blueFuel]['options'])
        pBlueOther = getGHGIParamsBlue(paramHandlerBlue, blueOptionsOther)
        GHGIBlueBase, _ = _getGHGIs(pBlue, pGreen, baseOnly=True)
        GHGIBlueOtherBase, _ = _getGHGIs(pBlueOther, pGreen, baseOnly=True)
        # ghgi0_1 + p_1 * ghgim_1 = ghgi0_2 + p_2 * ghgim_2
        # p_2 = (p_1*ghgim_1+ghgi0_1-ghgi0_2)/ghgim_2
        range2 = [(x * pBlue['mghgi'] + GHGIBlueBase - GHGIBlueOtherBase) / pBlueOther['mghgi'] for x in [xmin, xmax]]

        # add scatter traces
        x_vals = [pBlue['mlr'][0] * 100, xmax * (pBlue['mlr'][0] - range2[0]) / (range2[1] - range2[0]) * 100]
        y_val = sum(e['val'] for e in calcCost(paramHandlerGreen, 'GREEN', fuelSpecs[greenFuel]['options']).values()) \
                - sum(e['val'] for e in calcCost(paramHandlerBlue, 'BLUE', fuelSpecs[blueFuel]['options']).values())

        name = f"Comparing {fuelSpecs[blueFuel]['name']} with {fuelSpecs[greenFuel]['name']}"
        col = self.cfg['fscp_colour'][blueFuel.split('-')[-1] + '-' + greenFuel.split('-')[-1]]

        traces.append(go.Scatter(
            x=x_vals,
            y=[y_val] * 2,
            text=[f"{self.cfg['fuelYearTop']}, {gwp.upper()}" for gwp in [gwp, gwpOther]],
            textposition=['top right', 'top right'],
            textfont=dict(color=col),
            legendgroup=f"{blueFuel}--{greenFuel}",
            showlegend=False,
            marker_size=self._styles['highlight_marker_sm'],
            line_color=col,
            mode='markers+text',
            customdata=[self.cfg['fuelYearTop'], ],
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))

        annotations = []
        for i, gwpThis in enumerate([gwp, gwpOther]):
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

        shapes = []
        shapes.append(go.layout.Shape(
            type='line',
            xref='x2',
            yref='y2',
            x0=xmax * 100,
            y0=y_val,
            x1=xmin * 100,
            y1=y_val,
            line_color=col,
            line_width=self._styles['lw_thin'],
        ))

        return traces, range2, range3, annotations, shapes

    def __addFSCPSubplotContoursBottom(self, fuelSpecs: dict, blueFuel: str, greenFuel: str, xmin: float, xmax: float, zmin: float,
                                       zmax: float, colourscale: list, linedensity: float,params_options: dict):
        traces = []

        # uncomment below codes lines to set methane-leakage rate to zero in subplots (d) and (e)
        # fullParams = fullParams.copy()
        # fullParams.loc[fullParams['name'] == 'ghgi_ng_methaneleakage', 'value'] = 0.0

        # define data for plot grid
        share = np.linspace(xmin, xmax, self.cfg['plotting']['n_samples'])
        delta_cost = np.linspace(self.cfg['plotting']['yaxis1_min'], self.cfg['plotting']['yaxis1_max'],
                                 self.cfg['plotting']['n_samples'])

        # calculate GHGI data from params
        gwp = fuelSpecs[blueFuel]['options']['gwp']
        gwpOther = _otherGwp(gwp)
        greenOptionsOther = fuelSpecs[blueFuel]['options'].copy()
        greenOptionsOther['gwp'] = gwpOther

        currentParamsBlue = fuelSpecs[blueFuel]['params'].query(f"year=={self.cfg['fuelYearTop']}").droplevel(level=1)
        currentParamsGreen = fuelSpecs[greenFuel]['params'].query(f"year=={self.cfg['fuelYearTop']}").droplevel(level=1)

        paramHandlerBlue = ParameterHandler(currentParamsBlue, params_options)
        paramHandlerGreen = ParameterHandler(currentParamsGreen, params_options)

        pBlue = getGHGIParamsBlue(paramHandlerBlue, fuelSpecs[blueFuel]['options'])
        pGreen = getGHGIParamsGreen(paramHandlerGreen, fuelSpecs[greenFuel]['options'])

        # calculate FSCPs for grid
        share_v, delta_cost_v = np.meshgrid(share, delta_cost)
        pGreen['sh'] = (share_v, 0, 0)
        GHGIBlue, GHGIGreen = _getGHGIs(pBlue, pGreen)
        fscp = delta_cost_v / (GHGIBlue - GHGIGreen)

        # recolour the bit of the graph where emissions of green are higher than blue
        for x in range(len(share)):
            for y in range(len(delta_cost)):
                if GHGIGreen[x, y] > GHGIBlue:
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
        range3 = [GHGIGreen[0][0], GHGIGreen[0][-1]]

        pGreen = getGHGIParamsGreen(paramHandlerGreen, fuelSpecs[greenFuel]['options'])
        pGreenOther = getGHGIParamsGreen(paramHandlerGreen, greenOptionsOther)
        GHGIGreenBase, _ = _getGHGIs(pBlue, pGreen, baseOnly=True)
        GHGIGreenOtherBase, _ = _getGHGIs(pBlue, pGreenOther, baseOnly=True)
        # b_1 + eff*(sh1*ghgielre_1 + (1-sh1)*ghgielfos_1) = b_2 + eff*(sh2*ghgielre_2 + (1-sh2)*ghgielfos_2)
        # eff*sh2*(ghgielre_2-ghgielfos_2) = b_1-b_2 + eff*(ghgielfos_1-ghgielfos_2) + eff*sh1*(ghgielre_1-ghgielfos_1)
        # sh2 = (b_1-b_2 + eff*(ghgielfos_1-ghgielfos_2) + eff*sh1*(ghgielre_1-ghgielfos_1))/(eff*(ghgielre_2-ghgielfos_2))
        range2 = [(GHGIGreenBase - GHGIGreenOtherBase + pGreen['eff'] * (pGreen['elfos'][0] - pGreenOther['elfos'][0]) +
                   pGreen['eff'] * sh * (pGreen['elre'][0] - pGreen['elfos'][0])) /
                  (pGreenOther['eff'] * (pGreenOther['elre'][0] - pGreenOther['elfos'][0])) for sh in [xmin, xmax]]

        # add scatter traces
        x_val = pGreen['sh'] * 100
        y_val = sum(e['val'] for e in calcCost(paramHandlerGreen, 'GREEN', fuelSpecs[greenFuel]['options']).values()) \
                - sum(e['val'] for e in calcCost(paramHandlerBlue, 'BLUE', fuelSpecs[blueFuel]['options']).values())

        name = f"Comparing {fuelSpecs[blueFuel]['name']} with {fuelSpecs[greenFuel]['name']}"
        col = self.cfg['fscp_colour'][blueFuel.split('-')[-1] + '-' + greenFuel.split('-')[-1]]

        traces.append(go.Scatter(
            x=[x_val, ],
            y=[y_val],
            text=[self.cfg['fuelYearBottom'], ],
            textposition=["bottom right", "top right"],
            textfont=dict(color=col),
            legendgroup=f"{blueFuel}--{greenFuel}",
            showlegend=False,
            marker_size=self._styles['highlight_marker_sm'],
            line_color=col,
            mode='markers+text',
            customdata=[self.cfg['fuelYearBottom'], ],
            hovertemplate=f"<b>{name}</b> (%{{customdata}})<br>Carbon intensity difference: %{{x:.2f}}&plusmn;%{{error_x.array:.2f}}<br>"
                          f"Direct cost difference (w/o CP): %{{y:.2f}}&plusmn;%{{error_y.array:.2f}}<extra></extra>",
        ))

        return traces, range2, range3

    def __getXAxesStyle(self, calcedRanges: dict):
        vspace = self.cfg['vertical_spacing']

        # settings for x axes 1 to 15 (6 and 11 are undefined)
        axisSettings = [
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

        newAxes = {}
        for i, settings in enumerate(axisSettings):
            add, factor, side, anchor, overlay, position, standoff = settings

            if not add:
                continue

            axisName = f"xaxis{i + 1}"

            if axisName in calcedRanges:
                ran = [r * factor for r in calcedRanges[axisName]]
            else:
                ran = [self.cfg['plotting'][f"{axisName}_min"] * factor,
                       self.cfg['plotting'][f"{axisName}_max"] * factor]

            title = self.cfg['labels'][axisName]
            if i in [6, 7]:
                title = 38 * '&#160;' + title

            newAxes[axisName] = dict(
                title=title,
                range=ran,
                side=side,
                anchor=anchor,
            )

            if overlay is not None:
                newAxes[axisName]['overlaying'] = overlay

            if position is not None:
                newAxes[axisName]['position'] = position

            if standoff is not None:
                newAxes[axisName]['title'] = dict(text=title, standoff=standoff)

        newAxes['xaxis2']['dtick'] = 1.0
        newAxes['xaxis3']['dtick'] = 1.0

        newAxes['xaxis7']['ticklen'] = 25.0
        newAxes['xaxis7']['tick0'] = 0.0
        newAxes['xaxis7']['dtick'] = 0.5

        newAxes['xaxis8']['ticklen'] = 25.0
        newAxes['xaxis8']['tick0'] = 0.0
        newAxes['xaxis8']['dtick'] = 0.5

        newAxes['xaxis9']['ticklen'] = 25.0
        newAxes['xaxis10']['ticklen'] = 25.0

        return newAxes

    def __getColourScale(self):
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

def _convertFuelData(fuelData: pd.DataFrame, fuel_x: str, fuel_y: str):
    fuelData = fuelData[['fuel', 'type', 'year', 'cost', 'cost_uu', 'cost_ul', 'ghgi', 'ghgi_uu', 'ghgi_ul']]

    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')). \
        query(f"fuel_x=='{fuel_x}' & fuel_y=='{fuel_y}' & year_x==year_y"). \
        dropna()

    tmp['year'] = tmp['year_x']

    tmp['delta_cost'] = tmp['cost_y'] - tmp['cost_x']
    tmp['delta_cost_uu'] = tmp['cost_uu_y'] + tmp['cost_ul_x']
    tmp['delta_cost_ul'] = tmp['cost_ul_y'] + tmp['cost_uu_x']

    tmp['delta_ghgi'] = tmp['ghgi_x'] - tmp['ghgi_y']
    tmp['delta_ghgi_uu'] = tmp['ghgi_uu_x'] + tmp['ghgi_ul_y']
    tmp['delta_ghgi_ul'] = tmp['ghgi_ul_x'] + tmp['ghgi_uu_y']

    FSCPData = tmp[['fuel_x', 'delta_cost', 'delta_cost_uu', 'delta_cost_ul',
                    'delta_ghgi', 'delta_ghgi_uu', 'delta_ghgi_ul', 'year']]

    return FSCPData

def _getGHGIs(pBlue, pGreen, baseOnly=False):
    GHGIBlue = getGHGIBlue(**pBlue)
    GHGIGreen = getGHGIGreen(**pGreen)

    return sum(GHGIBlue[comp]['val'] for comp in GHGIBlue if not baseOnly or comp != 'scch4'), \
        sum(GHGIGreen[comp]['val'] for comp in GHGIGreen if not baseOnly or comp != 'elec')

def _getCostDiff(pBlue, pGreen):
    costBlue = getCostBlue(**pBlue)
    costGreen = getCostGreen(**pGreen)

    return sum(costBlue[comp]['val'] for comp in costGreen) - sum(costBlue[comp]['val'] for comp in costBlue)

def _otherGwp(gwp: str):
    return 'gwp20' if gwp == 'gwp100' else 'gwp100'
