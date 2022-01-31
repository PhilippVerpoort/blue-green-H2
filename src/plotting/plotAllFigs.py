import pandas as pd
import yaml

from src.plotting.plotFig1 import plotFig1
from src.plotting.plotFig2 import plotFig2
from src.plotting.plotFig3 import plotFig3
from src.plotting.plotFig4 import plotFig4
from src.plotting.plotFig5 import plotFig5
from src.plotting.plotFig6 import plotFig6
from src.plotting.plotFig7 import plotFig7
from src.plotting.plotFig8 import plotFig8


def plotAllFigs(fullParams: pd.DataFrame, fuelSpecs: dict, fuelData: pd.DataFrame, FSCPData: pd.DataFrame,
                fuelDataSteel: pd.DataFrame, FSCPDataSteel: pd.DataFrame, input_data: dict, plotting_cfg: dict,
                export_img=True):
    n_figs = len(plotting_cfg)
    pltCfg = {i: {**fuelSpecs, **yaml.load(plotting_cfg[f"fig{i}"], Loader=yaml.FullLoader)} for i in range (1, n_figs+1)}

    fig1 = plotFig1(fuelData, FSCPData, pltCfg[1], export_img=export_img)
    fig2 = plotFig2(fuelData, pltCfg[2], export_img=export_img)
    fig3 = plotFig3(FSCPData, FSCPDataSteel, pltCfg[3], export_img=export_img)
    fig4 = plotFig4(fuelData, fuelDataSteel, pltCfg[4], export_img=export_img)
    fig5 = plotFig5(fuelData, fullParams, input_data['fuels'], pltCfg[5], export_img=export_img)
    fig6 = plotFig6(fullParams, input_data['fuels'], pltCfg[6], export_img=export_img)
    fig7 = plotFig7(fuelData, pltCfg[7], export_img=export_img)
    fig8 = plotFig8(fuelData, pltCfg[8], export_img=export_img)

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8
