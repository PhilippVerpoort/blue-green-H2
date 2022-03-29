from typing import Union
import importlib

import pandas as pd
import yaml

from src.config_load import plots, plots_cfg_global


def plotAllFigs(fullParams: pd.DataFrame, fuelSpecs: dict, fuelData: pd.DataFrame, FSCPData: pd.DataFrame,
                fuelDataSteel: pd.DataFrame, FSCPDataSteel: pd.DataFrame, input_data: dict, plots_cfg: dict,
                plot_list: Union[list, None] = None, global_cfg = 'print'):

    allPlotArgs = {
        'plotBars': (fuelData,),
        'plotLines': (fuelData, FSCPData,),
        'plotOverTime': (FSCPData, FSCPDataSteel,),
        'plotHeatmap': (fuelData, fuelDataSteel,),
        'plotBlueGreen': (fuelData, fullParams, input_data['fuels']),
        'plotSensitivity': (fullParams, input_data['fuels'],),
        'plotSensitivityNG': (fuelData, fullParams,),
    }

    figs = {}
    for i, plotName in enumerate(plots):
        if plot_list is not None and plotName not in plot_list:
            if isinstance(plots[plotName], list):
                figs.update({f"{fig}": None for fig in plots[plotName]})
            elif isinstance(plots[plotName], dict):
                figs.update({f"{subFig}": None for fig in plots[plotName] for subFig in plots[plotName][fig]})
            else:
                raise Exception('Unknown figure type.')

        else:
            print(f"Plotting {plotName}...")
            plotArgs = allPlotArgs[plotName]
            config = yaml.load(plots_cfg[plotName], Loader=yaml.FullLoader)
            if 'import' in config:
                for imp in config['import']:
                    config[imp] = yaml.load(plots_cfg[imp], Loader=yaml.FullLoader)
            config = {**config, **fuelSpecs, **yaml.load(plots_cfg[plotName], Loader=yaml.FullLoader), **{'global': plots_cfg_global[global_cfg]}}

            module = importlib.import_module(f"src.plotting.plots.{plotName}")
            plotFigMethod = getattr(module, plotName)

            newFigs = plotFigMethod(*plotArgs, config)
            figs.update(newFigs)

    print('Done with plotting...')

    return figs
