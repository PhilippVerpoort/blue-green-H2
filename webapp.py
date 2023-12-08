#!/usr/bin/env python
from pathlib import Path

import plotly.io as pio
from dash.dependencies import Input, State
from piw import Webapp
from piw.template import piw_template

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


# change font in template
pio.templates['blue-green-H2'] = piw_template.update(layout=dict(font_family='Arial'))


# define webapp
webapp = Webapp(
    piw_id='blue-green-H2',
    title='On the cost competitiveness of blue and green hydrogen',
    pages={
        '': 'Simple',
        'advanced': 'Advanced',
    },
    desc='This webapp reproduces results presented in an accompanying manuscript on the cost competitiveness of blue'
         'and green hydrogen.',
    authors=['Philipp C. Verpoort', 'Falko Ueckerdt', 'Rahul Anantharaman', 'Christian Bauer', 'Fiona Beck',
             'Thomas Longden', 'Simon Roussanaly'],
    date='10/02/2022',
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
    sort_figs=['fig1', 'fig3', 'fig4', 'fig5', 'figS1', 'figS2', 'figS3', 'figS4', 'figS5'],
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
