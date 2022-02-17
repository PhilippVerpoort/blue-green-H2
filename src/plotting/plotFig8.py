import pandas as pd

from src.plotting.plotFig7 import plotFig7


def plotFig8(fuelData: pd.DataFrame, config: dict, export_img: bool = True):
    return plotFig7(fuelData, config, 'ghgi', export_img)
