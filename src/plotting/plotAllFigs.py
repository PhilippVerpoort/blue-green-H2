from typing import Union
import importlib

import pandas as pd
import yaml

from src.config_load import n_figs


def plotAllFigs(fullParams: pd.DataFrame, fuelSpecs: dict, fuelData: pd.DataFrame, FSCPData: pd.DataFrame,
                fuelDataSteel: pd.DataFrame, FSCPDataSteel: pd.DataFrame, input_data: dict, plotting_cfg: dict,
                export_img=True, plot_list: Union[list, None] = None):

    figArgs = [
        (fuelData, FSCPData),
        (fuelData,),
        (FSCPData, FSCPDataSteel),
        (fuelData, fuelDataSteel),
        (fuelData, fullParams, input_data['fuels']),
        (fullParams, input_data['fuels']),
        (fuelData,),
        (fuelData,),
    ]

    figs = []
    for i in range (1, n_figs+1):
        if plot_list is not None and f"fig{i}" not in plot_list:
            figs.append(None)
            continue

        config = {**fuelSpecs, **yaml.load(plotting_cfg[f"fig{i}"], Loader=yaml.FullLoader)}
        plotFigArgs = figArgs[i-1]

        module = importlib.import_module(f"src.plotting.plotFig{i}")
        plotFigMethod = getattr(module, f"plotFig{i}")

        figs.append(plotFigMethod(*plotFigArgs, config, export_img=export_img))

    return figs
