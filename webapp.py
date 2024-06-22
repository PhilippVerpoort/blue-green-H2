#!/usr/bin/env python
from pathlib import Path

import plotly.io as pio
from dash.dependencies import Input, State
from piw import Webapp
from piw.template import piw_template
from dash import html

from src.ctrls import main_ctrl, edit_tables_modal
from src.load import load_inputs
from src.plots.BarsPlot import BarsPlot
from src.plots.BlueGreenPlot import BlueGreenPlot
from src.plots.CostEmiOverTimePlot import CostEmiOverTimePlot
from src.plots.FSCPOverTimePlot import FSCPOverTimePlot
from src.plots.HeatmapPlot import HeatmapPlot
from src.plots.SensitivityPlot import SensitivityPlot
from src.proc import process_inputs
from src.update import update_inputs
from src.utils import load_yaml_config_file


# metadata
metadata = {
    'title': 'Interactive webapp for techno-economic analysis of the cost competitiveness of blue and green hydrogen',
    'abstract': 'This interactive webapp can be used to reproduce figures from an accompanying article by the same '
                'authors that studies the cost competitiveness of blue and green hydrogen. The figures compare cost, '
                'greenhouse-gas intensities, and resulting carbon cost (due to carbon pricing) obtained from '
                'techno-economic and life-cycle assessment of competing technologies that produce blue hydrogen (from '
                'natural gas with carbon capture) and green hydrogen (from renewable electricity via electrolysis). '
                'These figures allow to understand the long-term competitiveness of these two energy carriers and '
                'demonstrate how the bridging role of blue hydrogen is affected by residual emissions and high gas '
                'prices.',
    'about': html.Div([
        html.P('This interactive webapp can be used to reproduce figures from an accompanying article by the same '
               'authors that studies the cost competitiveness of blue and green hydrogen. Some of the key assumptions '
               '(e.g. methane leakage, electricity prices, electrolyser CAPEX, gas prices) can be changed here when '
               'generating the figures.'),
        html.P('We employ techno-economic and life-cycle assessments to compute the levelised costs and greenhouse-gas '
               'intensities of competing production technologies for blue (from natural gas with CCS) and green (from '
               'renewable electricity via electrolysis) hydrogen. This allows us to determine fuel-switching CO2 '
               'prices (FSCPs), defined by the carbon price at which fuels with lower emissions become cost '
               'competitive with fuels with higher emissions.'),
        html.P('Using these metrics, the presented figures compare the cost, greenhouse-gas intensities, and resulting '
               'FSCPs of competing fuels and technologies over the studied time range (2025 to 2050). These figures '
               'allow us to study whether and when green hydrogen becomes cost competitive with blue hydrogen. Our '
               'results demonstrate that the long-term competitiveness of blue hydrogen and its viability as a '
               'bridging option crucially depend on natural-gas prices and on residual emissions (non-captured CO2, '
               'upstream supply-chain CH4 and CO2).'),
        html.P('For more advanced changes and detailed information on the input data and methodology, we encourage '
               'users to inspect the article, its supplement, and the source code written in Python.'),
    ]),
    'authors': [
        {
            'first': 'Philipp C.',
            'last': 'Verpoort',
            'orcid': '0000-0003-1319-5006',
            'affiliation': ['Potsdam Institute for Climate Impact Research, Potsdam, Germany'],
        },
        {
            'first': 'Falko',
            'last': 'Ueckerdt',
            'orcid': '0000-0001-5585-030X',
            'affiliation': ['Potsdam Institute for Climate Impact Research, Potsdam, Germany'],
        },
        {
            'first': 'Rahul',
            'last': 'Anantharaman',
            'orcid': '0000-0001-9228-6197',
            'affiliation': ['SINTEF Energy Research, Gas Technology Department, Trondheim, Norway'],
        },
        {
            'first': 'Christian',
            'last': 'Bauer',
            'orcid': '0000-0002-1083-9200',
            'affiliation': ['Laboratory for Energy Systems Analysis, Paul Scherrer Institute (PSI), Villigen PSI, '
                            'Switzerland'],
        },
        {
            'first': 'Fiona',
            'last': 'Beck',
            'orcid': '0000-0001-9631-938X',
            'affiliation': ['School of Engineering, Australian National University, Acton ACT 2601, Canberra, '
                            'Australia'],
        },
        {
            'first': 'Thomas',
            'last': 'Longden',
            'orcid': '0000-0001-7593-659X',
            'affiliation': ['Urban Transformations Research Centre (UTRC), Western Sydney University, Parramatta, New '
                            'South Wales, Australia', 'Institute for Climate, Energy and Disaster Solutions (ICEDS), '
                            'Australian National University, Acton, Australian Capital Territory, Australia'],
        },
        {
            'first': 'Simon',
            'last': 'Roussanaly',
            'orcid': '0000-0002-4757-2829',
            'affiliation': 'SINTEF Energy Research, Gas Technology Department, Trondheim, Sør-Trondelag, Norway',
        },
    ],
    'date': '2023-12-09',
    'version': 'v3.0.3',
    'doi': '10.5880/pik.2023.006',
    'licence': {'name': 'CC BY 4.0', 'link': 'https://creativecommons.org/licenses/by/4.0/'},
    'citeas': 'Verpoort, Philipp C.; Ueckerdt, Falko; Anantharaman, Rahul; Bauer, Christian; Beck, Fiona; Longden, '
             'Thomas; Roussanaly, Simon (2023): Interactive webapp for techno-economic analysis of the cost '
             'competitiveness of blue and green hydrogen. V. 3.0.0. GFZ Data Services. '
             'https://doi.org/10.5880/pik.2023.006',
    'reference_citeas': 'Ueckerdt et al., On the cost competitiveness of blue and green hydrogen, Joule (2024).',
    'reference_doi': '10.1016/j.joule.2023.12.004',
}


# change font in template
pio.templates['blue-green-H2'] = piw_template.update(layout=dict(font_family='Arial'))


# define webapp
webapp = Webapp(
    piw_id='blue-green-H2',
    metadata=metadata,
    pages={
        '': 'Main',
        'supplementary': 'Supplementary',
    },
    load=[load_inputs],
    ctrls=[main_ctrl],
    generate_args=[
        Input('simple-update', 'n_clicks'),
        State('simple-important-params', 'data'),
        State('simple-gas-prices', 'data'),
        State('simple-gwp', 'value'),
    ],
    update=[update_inputs],
    ctrls_tables_modal=edit_tables_modal,
    proc=[process_inputs],
    plots=[CostEmiOverTimePlot, FSCPOverTimePlot, HeatmapPlot, SensitivityPlot, BarsPlot, BlueGreenPlot],
    sort_figs=['fig1', 'fig3', 'fig4', 'fig5', 'figS1', 'figS2', 'figS5', 'figS7'],
    glob_cfg=load_yaml_config_file('global'),
    styles=load_yaml_config_file('styles'),
    output=Path(__file__).parent / 'print',
    default_template='blue-green-H2',
    debug=False,
    input_caching=True,
)


# this will allow running the webapp locally
if __name__ == '__main__':
    webapp.start()
    webapp.run()
