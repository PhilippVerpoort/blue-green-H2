from typing import Union
import importlib

import pandas as pd
import yaml


def plotAllFigs(fullParams: pd.DataFrame, fuelSpecs: dict, fuelData: pd.DataFrame, FSCPData: pd.DataFrame,
                fuelDataSteel: pd.DataFrame, FSCPDataSteel: pd.DataFrame, input_data: dict, plotting_cfg: dict,
                export_img=True, plot_list: Union[list, None] = None):

    figArgs = [
        ('fig1ab', (fuelData,)),
        ('fig2', (fuelData, FSCPData,)),
        ('fig3', (FSCPData, FSCPDataSteel,)),
        ('fig4', (fuelData, fuelDataSteel,)),
        ('fig5', (fuelData, fullParams, input_data['fuels'],)),
        ('fig6', (fullParams, input_data['fuels'],)),
    ]

    figs = {}
    for plotName, plotArgs in figArgs:
        config = {**fuelSpecs, **yaml.load(plotting_cfg[plotName], Loader=yaml.FullLoader)}

        module = importlib.import_module(f"src.plotting.plot_{plotName}")
        plotFigMethod = getattr(module, f"plot_{plotName}")
        returnDummy = plot_list is not None and plotName not in plot_list

        newFigs = plotFigMethod(*plotArgs, config, export_img=export_img, rd=returnDummy)
        figs.update(newFigs)

    return figs
