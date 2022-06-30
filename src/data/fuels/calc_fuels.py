import pandas as pd

from src.data.fuels.calc_ghgi import calcGHGI
from src.data.fuels.calc_cost import calcCost
from src.data.params.full_params import getFullParams
from src.timeit import timeit


# calculate fuel data
@timeit
def calcFuelData(times: list, full_params: pd.DataFrame, fuels: dict, params: dict, gwp: str = 'gwp100', levelised: bool = False):
    fuelSpecs = {'names': {}, 'shortnames': {}, 'colours': {}}
    fuelEntries = []

    #print(full_params)

    for fuel_id, fuel in fuels.items():
        if 'cases' not in fuel:
            fuelSpecs['names'][fuel_id] = fuel['desc']
            fuelSpecs['shortnames'][fuel_id] = fuel['desc']
            fuelSpecs['colours'][fuel_id] = fuel['colour']

            fuelEntries.extend(__calcFuel(full_params, fuel_id, fuel, gwp, times))
        else:
            cases = __getCases(fuel['cases'], params, times)
            for cid, case in cases.items():
                fuel_id_full = f"{fuel_id}-{cid}"

                fuelSpecs['names'][fuel_id_full] = f"{fuel['desc']} ({case['desc']})"
                fuelSpecs['shortnames'][fuel_id_full] = f"{fuel['desc']}"
                fuelSpecs['colours'][fuel_id_full] = fuel['colour']

                overridden_names = case['params'].droplevel(level=1).index.unique().to_list()
                this_params = pd.concat([full_params.query(f"name not in @overridden_names"), case['params']])
                fuelEntries.extend(__calcFuel(this_params, fuel_id_full, fuel, gwp, times))

    fuelData = pd.DataFrame.from_records(fuelEntries)

    return fuelData, fuelSpecs


def __calcFuel(full_params, fuel_id, fuel, gwp, times):
    r = []

    for t in times:
        currentParams = full_params.query(f"year=={t}").droplevel(level=1)

        levelisedCost = calcCost(currentParams, fuel)
        levelisedGHGI = calcGHGI(currentParams, fuel, gwp)

        newFuel = {'fuel': fuel_id, 'type': fuel['type'], 'year': t}

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

        r.append(newFuel)

    return r


def __getCases(cases: dict, params: dict, times: list):
    overridden = {}

    for p in cases:
        overridden[p] = {}

        for c in cases[p]:
            new_param = {p: params[p]}
            new_param[p]['value'] = cases[p][c]['value']
            fuelParams = getFullParams(new_param, times)
            overridden[p][c] = {
                'desc': cases[p][c]['desc'],
                'params': fuelParams,
            }

    return __mergeCases(overridden)


def __mergeCases(overridden: dict):
    key = next(iter(overridden))
    entry = overridden[key]
    if len(overridden) == 1:
        return entry
    else:
        del overridden[key]
        r = __mergeCases(overridden)
        return {
            f"{c1}-{c2}": {
                'desc': f"{entry[c1]['desc']}, {r[c2]['desc']}",
                'params': pd.concat([entry[c1]['params'], r[c2]['params']]),
            }
            for c2 in r for c1 in entry
        }

