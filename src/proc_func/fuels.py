import copy

import numpy as np
import pandas as pd

from src.proc_func.cost import calc_cost
from src.proc_func.ghgi import calc_ghgi
from src.proc_func.helper import ParameterHandler
from src.proc_func.params import get_full_params


# calculate fuel data
def calc_fuel_data(times: list, full_params: pd.DataFrame, fuels: dict,
                   params: dict, gwp: str, params_options: dict, units: dict):
    fuel_entries = []
    fuel_specs = {}

    for fuel_id, fuel in fuels.items():
        if 'cases' not in fuel:
            options = {
                'blue_tech': fuel['blue_tech'] if 'blue_tech' in fuel else None,
                'gwp': gwp,
            }

            fuel_entries.extend(calc_fuel(full_params, fuel_id, fuel_id, options, times, params_options))

            fuel_specs[fuel_id] = {
                'name': fuel['name'],
                'type': fuel_id,
                'shortname': fuel['name'],
                'colour': fuel['colour'],
                'params': full_params,
                'options': options,
            }
        else:
            cases = _get_cases(fuel['cases'], params, times, units)
            for cid, case in cases.items():
                fuel_id_full = f"{fuel_id}-{cid}"

                options = {
                    'blue_tech': (case['blue_tech']
                                  if 'blue_tech' in case else
                                  fuel['blue_tech']
                                  if 'blue_tech' in fuel else
                                  None),
                    'gwp': gwp,
                }

                overridden_names = case['params'].droplevel(level=1).index.unique().to_list()
                this_params = pd.concat([full_params.query(f"name not in @overridden_names"), case['params']])
                fuel_entries.extend(calc_fuel(this_params, fuel_id_full, fuel_id, options, times, params_options))

                fuel_specs[fuel_id_full] = {
                    'name': f"{fuel['name']} ({case['desc']})",
                    'type': fuel_id,
                    'shortname': fuel['name'],
                    'colour': case['colour'] if 'colour' in case and case['colour'] else fuel['colour'],
                    'params': this_params,
                    'options': options,
                }

    return pd.DataFrame.from_records(fuel_entries), fuel_specs


def calc_fuel(full_params: pd.DataFrame, fuel_id_full: str, fuel_type: str,
              options: dict, times: list, params_options: dict):
    r = []

    for t in times:
        current_params = full_params.query(f"year=={t}").droplevel(level=1)
        param_handler = ParameterHandler(current_params, params_options)

        new_fuel = {'fuel': fuel_id_full, 'type': fuel_type, 'year': t}

        levelised_cost = calc_cost(param_handler, fuel_type, options)
        new_fuel |= _get_components(levelised_cost, 'cost')
        levelised_ghgi = calc_ghgi(param_handler, fuel_type, options)
        new_fuel |= _get_components(levelised_ghgi, 'ghgi')

        r.append(new_fuel)

    return r


def _get_components(levelised: dict, mode: str):
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


def _get_cases(cases: dict, params: dict, times: list, units: dict):
    overridden = {}

    for dim in cases:
        overridden[dim] = {}

        for c in cases[dim]:
            overridden[dim][c] = {
                'desc': cases[dim][c]['desc'],
                'colour': cases[dim][c]['colour'] if 'colour' in cases[dim][c] else None,
                'blue_tech': cases[dim][c]['blue_tech'] if 'blue_tech' in cases[dim][c] else None,
            }

            overridden_params = {p: copy.deepcopy(params[p]) for p in cases[dim][c] if p not in overridden[dim][c]}

            for p in overridden_params:
                overridden_params[p]['value'] = cases[dim][c][p]

            overridden[dim][c]['params'] = get_full_params(overridden_params, units, times)

    return _merge_cases(overridden)


def _merge_cases(overridden: dict):
    key = next(iter(overridden))
    entry = overridden[key]
    if len(overridden) == 1:
        return entry
    else:
        del overridden[key]
        r = _merge_cases(overridden)
        return {
            '-'.join([c for c in [c1, c2] if not c == 'none']): {
                'desc': f"{entry[c1]['desc']}, {r[c2]['desc']}",
                'colour': entry[c1]['colour'] if entry[c1]['colour'] else r[c2]['colour'],
                'params': pd.concat([entry[c1]['params'], r[c2]['params']]),
                'blue_tech': (r[c2]['blue_tech']
                              if 'blue_tech' in r[c2] and r[c2]['blue_tech'] else
                              entry[c1]['blue_tech']),
            }
            for c2 in r for c1 in entry
        }
