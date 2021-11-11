import math

import pandas as pd

from src.data.calc_ci import calcCI
from src.data.calc_cost import calcCost


# calculate fuel data
def calcFuelData(times: list, full_params: pd.DataFrame, fuels: dict, gwp: str = 'gwp100', levelised: bool = False):
    fuelData = pd.DataFrame(columns=['fuel', 'year', 'cost', 'cost_u', 'ci', 'ci_u'])

    fuelSpecs = {'names': {}, 'colours': {}}

    for fuel_id, fuel in fuels.items():
        fuelSpecs['names'][fuel_id] = fuel['desc']
        fuelSpecs['colours'][fuel_id] = fuel['colour']

        for t in times:
            currentParams = getCurrentAsDict(full_params, t)

            levelisedCost = calcCost(currentParams, fuel)
            levelisedCI = calcCI(currentParams, fuel, gwp)

            cost = sum(levelisedCost[component][0] for component in levelisedCost)
            ci = sum(levelisedCI[component][0] for component in levelisedCI)
            cost_u = math.sqrt(sum((levelisedCost[component][1])**2 for component in levelisedCost))
            ci_u = math.sqrt(sum((levelisedCI[component][1])**2 for component in levelisedCI))

            newFuel = {'fuel': fuel_id, 'year': t, 'cost': cost, 'cost_u': cost_u, 'ci': ci, 'ci_u': ci_u}

            if levelised:
                for component in levelisedCost:
                    newFuel[f"cost__{component}"] = levelisedCost[component][0]
                    newFuel[f"cost_u__{component}"] = levelisedCost[component][1]
                for component in levelisedCI:
                    newFuel[f"ci__{component}"] = levelisedCI[component][0]
                    newFuel[f"ci_u__{component}"] = levelisedCI[component][1]

            fuelData = fuelData.append(newFuel, ignore_index=True)

    return fuelData, fuelSpecs


# convert dataframe of parameters/coefficients to a simple dict
def getCurrentAsDict(full_data: pd.DataFrame, t: int):
    currentData = {}

    for p in list(full_data.query("year == {}".format(t)).name):
        currentData[p] = full_data.query("year == {} & name == '{}'".format(t, p)).iloc[0].value

    return currentData
