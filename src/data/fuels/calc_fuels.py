import numpy as np
import pandas as pd

from src.data.fuels.calc_cost import calcCost
from src.data.fuels.calc_ghgi import calcGHGI
from src.data.params.full_params import getFullParams
from src.timeit import timeit


# calculate fuel data
@timeit
def calcFuelData(times: list, full_params: pd.DataFrame, fuels: dict, params: dict, gwp: str):
    fuelEntries = []
    fuelSpecs = {}

    for fuel_id, fuel in fuels.items():
        if 'cases' not in fuel:
            options = {
                'blue_tech': fuel['blue_tech'] if 'blue_tech' in fuel else None,
                'gwp': gwp,
            }

            fuelEntries.extend(__calcFuel(full_params, fuel_id, fuel_id, options, times))

            fuelSpecs[fuel_id] = {
                'name': fuel['name'],
                'type': fuel_id,
                'shortname': fuel['name'],
                'colour': fuel['colour'],
                'params': full_params,
                'options': options,
            }
        else:
            cases = __getCases(fuel['cases'], params, times)
            for cid, case in cases.items():
                fuel_id_full = f"{fuel_id}-{cid}"

                options = {
                    'blue_tech': case['blue_tech'] if 'blue_tech' in case else fuel['blue_tech'] if 'blue_tech' in fuel else None,
                    'gwp': gwp,
                }

                overridden_names = case['params'].droplevel(level=1).index.unique().to_list()
                this_params = pd.concat([full_params.query(f"name not in @overridden_names"), case['params']])
                fuelEntries.extend(__calcFuel(this_params, fuel_id_full, fuel_id, options, times))

                fuelSpecs[fuel_id_full] = {
                    'name': f"{fuel['name']} ({case['desc']})",
                    'type': fuel_id,
                    'shortname': fuel['name'],
                    'colour': case['colour'] if 'colour' in case and case['colour'] else fuel['colour'],
                    'params': this_params,
                    'options': options,
                }

    return pd.DataFrame.from_records(fuelEntries), fuelSpecs


def __calcFuel(full_params: pd.DataFrame, fuel_id_full: str, type: str, options: dict, times: list):
    r = []

    for t in times:
        currentParams = full_params.query(f"year=={t}").droplevel(level=1)

        newFuel = {'fuel': fuel_id_full, 'type': type, 'year': t}

        levelisedCost = calcCost(currentParams, type, options)
        newFuel |= __getComponents(levelisedCost, 'cost')
        levelisedGHGI = calcGHGI(currentParams, type, options)
        newFuel |= __getComponents(levelisedGHGI, 'ghgi')

        r.append(newFuel)

    return r


def __getComponents(levelised: dict, mode: str):
    r = {}

    # value components
    r_val = {}
    for component in levelised:
        r_val[f"{mode}__{component}"] = levelised[component]['val']

    # value total
    r_val[mode] = sum(c for c in r_val.values())

    r |= r_val

    # uncertainty total and parameter-specific components
    for ut in ['uu', 'ul']:
        r_unc = {}
        for component in levelised:
            for pname in levelised[component][ut]:
                varname = f"{mode}_{ut}__{pname}"
                if varname not in r_unc:
                    r_unc[varname] = levelised[component][ut][pname]
                else:
                    r_unc[varname] += levelised[component][ut][pname]

        r_unc[f"{mode}_{ut}"] = np.sqrt(sum(c**2 for c in r_unc.values()))

        r |= r_unc

    return r


def __getCases(cases: dict, params: dict, times: list):
    overridden = {}

    for dim in cases:
        overridden[dim] = {}

        for c in cases[dim]:
            overridden[dim][c] = {
                'desc': cases[dim][c]['desc'],
                'colour': cases[dim][c]['colour'] if 'colour' in cases[dim][c] else None,
                'blue_tech': cases[dim][c]['blue_tech'] if 'blue_tech' in cases[dim][c] else None,
            }

            overridden_params = {p: params[p] for p in cases[dim][c] if p not in overridden[dim][c]}

            for p in overridden_params:
                overridden_params[p]['value'] = cases[dim][c][p]

            overridden[dim][c]['params'] = getFullParams(overridden_params, times)

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
            '-'.join([c for c in [c1, c2] if not c == 'none']): {
                'desc': f"{entry[c1]['desc']}, {r[c2]['desc']}",
                'colour': entry[c1]['colour'] if entry[c1]['colour'] else r[c2]['colour'],
                'blue_tech': r[c2]['blue_tech'] if 'blue_tech' in r[c2] and r[c2]['blue_tech'] else entry[c1]['blue_tech'],
                'params': pd.concat([entry[c1]['params'], r[c2]['params']]),
            }
            for c2 in r for c1 in entry
        }

