from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from src.data.fuels.calc_fuels import calcFuel
from src.utils import load_yaml_plot_config_file
from src.plots.BasePlot import BasePlot


class CostEmiOverTimePlot(BasePlot):
    figs, cfg = load_yaml_plot_config_file('CostEmiOverTimePlot')

    def plot(self, inputs: dict, outputs: dict, subfig_names: list) -> dict:
        ret = {}

        # produce figures
        for sub, type in [('A', 'cost'), ('B', 'ghgi')]:
            subfigName = f"fig1{sub}"

            # check if plotting is needed
            if subfigName not in subfig_names:
                ret.update({subfigName: None})
                continue

            # plot subfigure
            subcfg = self._subfig_cfgs[subfigName]
            subfig = self._produceFigure(outputs['fuelData'], outputs['fuelSpecs'], subcfg, type,
                                         inputs['params_options'])

            ret.update({subfigName: subfig})

        if 'figS5' in subfig_names:
            type = 'cost'
            subcfg = self._subfig_cfgs['fig1A'] | self._subfig_cfgs['figS5']
            ret['figS5'] = self._produceFigure(outputs['fuelData'], outputs['fuelSpecs'], subcfg, type,
                                               inputs['params_options'], with_iea=True, iea_data=inputs['iea_data'],
                                               cost_h2transp=outputs['fullParams'].loc['cost_h2transp'])

        return self.add_gwp_label(inputs['options']['gwp'], ret)


    def _produceFigure(self, plotData: pd.DataFrame, fuelSpecs: dict, subConfig: dict, type: str, params_options: dict,
                       with_iea: bool = False, iea_data: Optional[pd.DataFrame] = None,
                       cost_h2transp: Optional[pd.DataFrame] = None):
        scale = 1.0 if type == 'cost' else 1000.0


        # create figure
        fig = go.Figure()


        for cID, corridor in subConfig['showCorridors'].items():
            corrCases = corridor['cases']
            corrColour = corridor['colour'] if 'colour' in corridor else fuelSpecs[list(corrCases.keys())[0].replace('-gwpOther', '')]['colour']

            allCases = list(corrCases.keys()) + [cExt for c in corrCases.values() for cExt in (c['extended'] if 'extended' in c else [])]
            casesColours = {c: corrCases[c.replace('-gwpOther', '')]['colour'] if 'colour' in corrCases[c] else fuelSpecs[c.replace('-gwpOther', '')]['colour'] for c in allCases}
            caseGroupLabel = fuelSpecs[allCases[0].replace('-gwpOther', '')]['shortname']
            casesLabels = {c: corrCases[c]['desc'] if 'desc' in corrCases[c] else fuelSpecs[c.replace('-gwpOther', '')]['name'] for c in allCases}

            legendID = cID.rstrip('-')[0]

            # select data and determine max and min of corridor
            thisData = self._getThisData(plotData, fuelSpecs, corrCases, params_options)

            thisData['upper'] = thisData[type] + thisData[type + '_uu']
            thisData['lower'] = thisData[type] - thisData[type + '_ul']

            thisData_max = thisData.groupby('year')['upper'].max().reset_index()
            thisData_min = thisData.groupby('year')['lower'].min().reset_index()

            # add corridor
            fig.add_trace(go.Scatter(
                # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                x=thisData_min.year,
                y=thisData_min['lower']*scale,
                legendgroup=legendID,
                mode='lines',
                line=dict(color=corrColour, width=self._styles['lw_thin'] if subConfig['showLines'] else 0.0),
                showlegend=False,
                hoverinfo='none',
            ))

            fig.add_trace(go.Scatter(
                x=thisData_max.year,
                y=thisData_max['upper']*scale,
                fill='tonexty', # fill area between traces
                mode='lines',
                legendgroup=legendID,
                line=dict(color=corrColour, width=self._styles['lw_thin'] if subConfig['showLines'] else 0.0),
                fillpattern=dict(shape='/') if cID.endswith('-gwpOther') else None,
                fillcolor=("rgba({}, {}, {}, {})".format(*hex_to_rgb(corrColour), .3)),
                showlegend=False,
                hoverinfo='none',
            ))

            # add lines
            for c in corrCases:
                cData = self._getThisData(thisData, fuelSpecs, [c], params_options)

                fig.add_trace(go.Scatter(
                    # The minimum (or maximum) line needs to be added before the below area plot can be applied.
                    x=cData.year,
                    y=cData[type]*scale,
                    legendgrouptitle=dict(text=f"<b>{caseGroupLabel}</b>"),
                    legendgroup=legendID,
                    mode='lines',
                    name=casesLabels[c],
                    line=dict(color=casesColours[c], width=self._styles['lw_thin'], dash='dot' if c.endswith('-gwpOther') else None),
                    showlegend=True,
                    hovertemplate=f"<b>{casesLabels[c]}</b><br>Time: %{{x:.2f}}<br>{subConfig['label']}: %{{y:.2f}}<extra></extra>",
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
            text=subConfig['label'],
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
            yaxis=dict(title=subConfig['yaxislabel'], zeroline=True, range=[0, subConfig['ymax']*scale]),
            legend_title='',
        )
        fig.update_yaxes(rangemode= "tozero")

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
            for k, ((tech, subtech), rows) in enumerate(iea_data.groupby(['technology', 'subtechnology'], dropna=False)):
                rows_withtd = rows \
                    .merge(cost_h2transp['val'].to_frame('cost_h2transp').rename_axis('period').reset_index(), on='period', how='outer') \
                    .set_index('period') \
                    .sort_index() \
                    .assign(cost_h2transp=lambda df: df['cost_h2transp'].bfill()) \
                    .dropna(subset='value') \
                    .assign(value=lambda df: df['value'] + df['cost_h2transp']) \
                    .drop(columns='cost_h2transp') \
                    .reset_index()
                plot_data = rows_withtd \
                    .groupby('period')['value'] \
                    .agg(['mean', 'max']) \
                    .assign(delta=lambda df: df['max'] - df['mean']) \
                    .reset_index()
                colour = subConfig['iea_colours'][tech] if tech == 'Blue' else subConfig['iea_colours'][tech][subtech]
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
                    name=f"{tech} H<sub>2</sub>" if not isinstance(subtech, str) else f"{tech} H<sub>2</sub><br>({subtech})",
                ))

            fig.update_layout(
                xaxis_range=[2021.5, 2050.0],
                yaxis_range=[0.0, subConfig['ymaxS5']],
            )

        return fig


    def _getThisData(self, plotData: pd.DataFrame, fuelSpecs: dict, cases: list, params_options: dict):
        ret = []

        for c in cases:
            if c.endswith('gwpOther'):
                c = c.replace('-gwpOther', '')
                options = fuelSpecs[c]['options'].copy()
                options['gwp'] = 'gwp20' if options['gwp']=='gwp100' else 'gwp100'
                ret.append(
                    pd.DataFrame.from_records(calcFuel(fuelSpecs[c]['params'], c+'-gwpOther', fuelSpecs[c]['type'],
                                                       options, plotData.year.unique(), params_options))
                )
            else:
                ret.append(
                    plotData.query(f"fuel=='{c}'").reset_index(drop=True)
                )

        return pd.concat(ret)
