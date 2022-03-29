import pandas as pd

from src.data.fuels.calc_ghgi import calcGHGI
from src.data.fuels.calc_cost import calcCost
from src.timeit import timeit


# calculate fuel data
@timeit
def calcFuelData(times: list, full_params: pd.DataFrame, fuels: dict, gwp: str = 'gwp100', levelised: bool = False):
    fuelSpecs = {'names': {}, 'colours': {}}
    fuelEntries = []

    for fuel_id, fuel in fuels.items():
        fuelSpecs['names'][fuel_id] = fuel['desc']
        fuelSpecs['colours'][fuel_id] = fuel['colour']

        for t in times:
            currentParams = full_params.query(f"year=={t}").droplevel(level=1)

            levelisedCost = calcCost(currentParams, fuel)
            levelisedGHGI = calcGHGI(currentParams, fuel, gwp)

            newFuel = {'fuel': fuel_id, 'type': fuels[fuel_id]['type'], 'year': t}

            for component in levelisedCost:
                newFuel[f"cost__{component}"] = levelisedCost[component][0]
                newFuel[f"cost_uu__{component}"] = levelisedCost[component][1]
                newFuel[f"cost_ul__{component}"] = levelisedCost[component][2]
            for component in levelisedGHGI:
                newFuel[f"ghgi__{component}"] = levelisedGHGI[component][0]
                newFuel[f"ghgi_uu__{component}"] = levelisedGHGI[component][1]
                newFuel[f"ghgi_ul__{component}"] = levelisedGHGI[component][2]

            newFuel['cost'] = sum(newFuel[f"cost__{component}"] for component in levelisedCost)
            newFuel['cost_uu'] = sum(newFuel[f"cost_uu__{component}"] for component in levelisedCost)
            newFuel['cost_ul'] = sum(newFuel[f"cost_ul__{component}"] for component in levelisedCost)

            newFuel['ghgi'] = sum(newFuel[f"ghgi__{component}"] for component in levelisedGHGI)
            newFuel['ghgi_uu'] = sum(newFuel[f"ghgi_uu__{component}"] for component in levelisedGHGI)
            newFuel['ghgi_ul'] = sum(newFuel[f"ghgi_ul__{component}"] for component in levelisedGHGI)

            fuelEntries.append(newFuel)

    fuelData = pd.DataFrame.from_records(fuelEntries)

    return fuelData, fuelSpecs
