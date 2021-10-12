import pandas as pd

from src.calc_ci import calcCI
from src.calc_cost import calcCost


# calculate fuel data
def calcFuelData(full_params: pd.DataFrame, full_coeffs: pd.DataFrame, fuels: dict, consts: dict, times: list):
    fuelData = pd.DataFrame(columns=['fuel', 'year', 'cost', 'ci'])

    for fuel_id, fuel in fuels.items():
        for t in times:
            currentParams = __getCurrentAsDict(full_params, t)
            currentCoeffs = __getCurrentAsDict(full_coeffs, t)

            fuel_cost = calcCost(currentParams, currentCoeffs, fuel, consts)
            fuel_ci = calcCI(currentParams, currentCoeffs, fuel, consts)

            new_fuel = {'fuel': fuel_id, 'year': t, 'cost': fuel_cost, 'ci': fuel_ci}
            fuelData = fuelData.append(new_fuel, ignore_index=True)

    return fuelData


# convert dataframe of parameters/coefficients to a simple dict
def __getCurrentAsDict(full_data: pd.DataFrame, t: int):
    currentData = {}

    for p in list(full_data.query("year == {}".format(t)).name):
        currentData[p] = full_data.query("year == {} & name == '{}'".format(t, p)).iloc[0].value

    return currentData