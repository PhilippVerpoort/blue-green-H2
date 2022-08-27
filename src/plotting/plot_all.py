from typing import Union
import importlib

import yaml
import plotly.io as pio
import plotly.graph_objects as go

from src.config_load import plots, plots_cfg_global
from src.config_load_app import app_cfg
from src.plotting.styling.template import defineTemplate


pio.templates['pik'] = defineTemplate()


def plotAllFigs(allData: dict, input_data: dict, plots_cfg: dict,
                figs_needed: Union[list, None] = None, global_cfg='print'):

    # determine which plots need to be run based on the figures that are needed
    plotsNeeded = {
        plotName: [subfig for fig, subfigs in figs.items() if (figs_needed is None or fig in figs_needed) for subfig in subfigs]
        for plotName, figs in plots.items()
    }

    # collect args for plot functions from data
    allPlotArgs = {
        'plotBars': (allData['fuelData'],),
        'plotBlueGreen': (allData['fuelData'],),
        'plotCostAndEmiOverTime': (allData['fuelData'],),
        'plotHeatmap': (allData['fuelData'],),
        'plotLines': (allData['fuelData'], allData['FSCPData'],),
        'plotOverTime': (allData['FSCPData'],),
        'plotSensitivityFSCP': (input_data['fuels'],),
    }

    # set default theme
    pio.templates.default = "pik"

    ret = {}
    for i, plotName in enumerate(plots):
        if plotName not in plotsNeeded or not plotsNeeded[plotName]:
            ret.update({f"{subFig}": None for fig in plots[plotName] for subFig in plots[plotName][fig]})
        else:
            print(f"Plotting {plotName}...")

            # get plot args
            plotArgs = allPlotArgs[plotName]

            # get plot config
            config = yaml.load(plots_cfg[plotName], Loader=yaml.FullLoader)
            if 'import' in config:
                for imp in config['import']:
                    config[imp] = yaml.load(plots_cfg[imp], Loader=yaml.FullLoader)
            config = {**config, 'fuelSpecs': allData['fuelSpecs'], 'global': plots_cfg_global[global_cfg]}

            # load and execute plot function
            module = importlib.import_module(f"src.plotting.plots.{plotName}")
            plotFunc = getattr(module, plotName)

            # execute plot function
            newFigs = plotFunc(*plotArgs, config, plotsNeeded[plotName], is_webapp=(global_cfg=='webapp'))
            ret.update(newFigs)

    print('Plot creation complete...')

    # insert empty figure for 'None' values
    if global_cfg=='webapp':
        for subfig in ret:
            if ret[subfig] is None:
                if any(subfig in fs[fig] for plotName, fs in plots.items() for fig in fs if fig in app_cfg['figures']):
                    ret[subfig] = go.Figure()

    return {subfigName: subfig for subfigName, subfig in ret.items() if subfig is not None}
