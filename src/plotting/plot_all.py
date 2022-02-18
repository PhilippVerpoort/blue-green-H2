from typing import Union
import importlib

import pandas as pd
import yaml


def plotAllFigs(fullParams: pd.DataFrame, fuelSpecs: dict, fuelData: pd.DataFrame, FSCPData: pd.DataFrame,
                fuelDataSteel: pd.DataFrame, FSCPDataSteel: pd.DataFrame, input_data: dict, plotting_cfg: dict,
                export_img=True, plot_list: Union[list, None] = None):

    allPlotArgs = [
        (fuelData,),
        (fuelData, FSCPData,),
        (FSCPData, FSCPDataSteel,),
        (fuelData, fuelDataSteel,),
        (fuelData, fullParams, input_data['fuels']),
        (fullParams, input_data['fuels'],),
    ]

    figs = {}
    for i, plotName in enumerate(plotting_cfg):
        plotArgs = allPlotArgs[i]
        config = {**fuelSpecs, **yaml.load(plotting_cfg[plotName], Loader=yaml.FullLoader)}

        module = importlib.import_module(f"src.plotting.plot_{plotName}")
        plotFigMethod = getattr(module, f"plot_{plotName}")
        returnDummy = plot_list is not None and plotName not in plot_list

        newFigs = plotFigMethod(*plotArgs, config, export_img=export_img, rd=returnDummy)
        figs.update(newFigs)

    return figs
