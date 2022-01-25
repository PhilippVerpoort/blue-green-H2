import re
from typing import Union

import yaml
from dash.exceptions import PreventUpdate


# simple update
def updateScenarioInputSimple(scenarioInput: dict,
                              simple_gwp: str, simple_leakage: float, simple_ng_price: float, simple_lifetime: int, simple_irate: float,
                              simple_cost_green_capex_2020: float, simple_cost_green_capex_2050: float,
                              simple_cost_green_elec_2020: float, simple_cost_green_elec_2050: float,
                              simple_ghgi_green_elec: str, simple_green_ocf: int,
                              simple_cost_blue_capex_heb: float, simple_cost_blue_capex_leb: float,
                              simple_cost_blue_cts_2020: float, simple_cost_blue_cts_2050: float,
                              simple_blue_eff_heb: float, simple_blue_eff_leb: float,
                              advanced_gwp: str, advanced_times: list, advanced_fuels: list, advanced_params: list):
    # update gwp option
    scenarioInput['options']['gwp'] = simple_gwp

    # define dict containing all value updates
    allUpdates = {
        # general options
        'ghgi_ng_methaneleakage': {2050: simple_leakage},
        'cost_ng_price': {2025: simple_ng_price, 2050: simple_ng_price},
        'lifetime': simple_lifetime,
        'irate': simple_irate,

        # green data
        'cost_green_capex': {2020: simple_cost_green_capex_2020, 2050: simple_cost_green_capex_2050},
        'cost_green_elec': {'RE': {2020: simple_cost_green_elec_2020, 2050: simple_cost_green_elec_2050}},
        'ghgi_green_elec': {'RE': {simple_gwp: {2025: simple_ghgi_green_elec, 2050: simple_ghgi_green_elec}}},
        'green_ocf': simple_green_ocf,

        # blue data
        'cost_blue_capex': {
            'smr+lcrccs': {
                2020: simple_cost_blue_capex_heb,
                2050: simple_cost_blue_capex_heb,
            },
            'atr+hcrccs': {
                2025: simple_cost_blue_capex_leb,
                2030: simple_cost_blue_capex_leb,
                2050: simple_cost_blue_capex_leb,
            },
        },
        'cost_blue_cts': {
            2020: simple_cost_blue_cts_2020,
            2050: simple_cost_blue_cts_2050,
        },
        'cost_blue_eff': {
            'smr+lcrccs': simple_blue_eff_heb,
            'atr+hcrccs': simple_blue_eff_leb,
        },
    }

    # make updates accordingly
    for paramKey, field in allUpdates.items():
        __updateParameter(scenarioInput['params'][paramKey], {'value': field})

    return scenarioInput


# function to update parameter value based on field from above
def __updateParameter(param, field):
    if not isinstance(param, dict):
        raise Exception('Cannot update value. This should be a dict.')

    for key, val in field.items():
        if isinstance(param[key], dict):
            __updateParameter(param[key], val)
        elif isinstance(param[key], float) or isinstance(param[key], int):
            param[key] = val
        elif isinstance(param[key], str):
            param[key] = __replaceValue(val, param[key])
        else:
            raise Exception('Unknown type of value variable.')


# update parameter in case it's a string containing uncertainty values
def __replaceValue(new_value: Union[int, float], param: str):
    if ' +- ' in param:
        nums = param.split(' +- ')
        uncertainty = float(nums[1])
        return f"{new_value} +- {uncertainty}"
    elif ' + ' in param and ' - ' in param:
        nums = re.split(r" [+-] ", param)
        uncertainty = float(nums[1])
        uncertainty_lower = float(nums[2])
        return f"{new_value} + {uncertainty} - {uncertainty_lower}"
    else:
        raise Exception('Incorrect syntax for uncertainty.')


# advanced update
def updateScenarioInputAdvanced(scenarioInput: dict,
                                simple_gwp: str, simple_leakage: float, simple_ng_price: float, simple_lifetime: int, simple_irate: float,
                                simple_cost_green_capex_2020: float, simple_cost_green_capex_2050: float,
                                simple_cost_green_elec_2020: float,  simple_cost_green_elec_2050: float,
                                simple_ghgi_green_elec: str, simple_green_ocf: int,
                                simple_cost_blue_capex_heb: float, simple_cost_blue_capex_leb: float,
                                simple_cost_blue_cts_2020: float, simple_cost_blue_cts_2050: float,
                                simple_cost_blue_eff_heb: float, simple_cost_blue_eff_leb: float,
                                advanced_gwp: str, advanced_times: list, advanced_fuels: list, advanced_params: list):
    # update GWP
    scenarioInput['options']['gwp'] = advanced_gwp

    # update times:
    scenarioInput['options']['times'] = []
    for item in advanced_times:
        try:
            t = int(item['i'])
        except Exception:
            raise PreventUpdate()
        scenarioInput['options']['times'].append(t)

    scenarioInput['fuels'] = {}
    for row in advanced_fuels:
        newFuel = {
            'desc': row['desc'],
            'type': row['type'],
            'colour': row['colour'],
            'blue_type': row['blue_type'],
            'include_capex': row['include_capex'],
            'elecsrc': row['elecsrc']
        }

        scenarioInput['fuels'][row['fuel']] = newFuel

    scenarioInput['params'] = {}
    for row in advanced_params:
        newParam = {
            'desc': row['desc'],
            'type': row['type'],
            'unit': row['unit'],
        }

        if isinstance(row['value'], str) and ':' in row['value']:
            newParam['value'] = yaml.load(row['value'], Loader=yaml.FullLoader)
        else:
            newParam['value'] = row['value']

        scenarioInput['params'][row['param']] = newParam


    return scenarioInput
