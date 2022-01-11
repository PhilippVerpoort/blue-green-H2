import math

import pandas as pd

from src.data.calc_ci import calcCI
from src.data.calc_cost import calcCost


# calculate fuel data
def calcFuelData(times: list, full_params: pd.DataFrame, fuels: dict, gwp: str = 'gwp100', levelised: bool = False):
    fuelData = pd.DataFrame(columns=['fuel', 'year', 'cost', 'cost_uu', 'cost_ul', 'ci', 'ci_uu', 'ci_ul'])

    fuelSpecs = {'names': {}, 'colours': {}}

    for fuel_id, fuel in fuels.items():
        fuelSpecs['names'][fuel_id] = fuel['desc']
        fuelSpecs['colours'][fuel_id] = fuel['colour']

        for t in times:
            currentParams = getCurrentAsDict(full_params, t)

            levelisedCost = calcCost(currentParams, fuel)
            levelisedCI = calcCI(currentParams, fuel, gwp)

            newFuel = {'fuel': fuel_id, 'year': t}

            newFuel['cost'] = sum(levelisedCost[component][0] for component in levelisedCost)
            newFuel['cost_uu'] = sum(levelisedCost[component][1] for component in levelisedCost)
            newFuel['cost_ul'] = sum(levelisedCost[component][2] for component in levelisedCost)

            newFuel['ci'] = sum(levelisedCI[component][0] for component in levelisedCI)
            newFuel['ci_uu'] = sum(levelisedCI[component][1] for component in levelisedCI)
            newFuel['ci_ul'] = sum(levelisedCI[component][2] for component in levelisedCI)

            if levelised:
                for component in levelisedCost:
                    newFuel[f"cost__{component}"] = levelisedCost[component][0]
                    newFuel[f"cost_uu__{component}"] = levelisedCost[component][1]
                    newFuel[f"cost_ul__{component}"] = levelisedCost[component][2]
                for component in levelisedCI:
                    newFuel[f"ci__{component}"] = levelisedCI[component][0]
                    newFuel[f"ci_uu__{component}"] = levelisedCI[component][1]
                    newFuel[f"ci_ul__{component}"] = levelisedCI[component][2]

            fuelData = fuelData.append(newFuel, ignore_index=True)

    return fuelData, fuelSpecs


# convert dataframe of parameters/coefficients to a simple dict
def getCurrentAsDict(full_data: pd.DataFrame, t: int):
    currentDataValue = {}
    currentDataUncUp = {}
    currentDataUncLo = {}

    for p in list(full_data.query("year == {}".format(t)).name):
        datum = full_data.query("year == {} & name == '{}'".format(t, p)).iloc[0]
        currentDataValue[p] = datum.value
        currentDataUncUp[p] = datum.uncertainty if datum.isnull().uncertainty is not None else 0.0
        currentDataUncLo[p] = datum.uncertainty_lower if not datum.isnull().uncertainty_lower else \
                              datum.uncertainty if datum.isnull().uncertainty is not None else 0.0

    return currentDataValue, currentDataUncUp, currentDataUncLo
