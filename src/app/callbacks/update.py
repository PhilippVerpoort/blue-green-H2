import re
from typing import Union

import yaml
from dash.exceptions import PreventUpdate

from src.data.params.full_params import convertValue


# simple update
def updateScenarioInputSimple(scenarioInput: dict, simple_gwp: str, simple_important_params: list):
    # update gwp option
    scenarioInput['options']['gwp'] = simple_gwp

    # update important params
    for entry in simple_important_params:
        value_old = scenarioInput['params'][entry['name']]['value']
        value_new = {2025: entry['val_2025'], 2050: entry['val_2050']}

        if entry['name'] == 'cost_green_elec':
            value_old = value_old['RE']
            value_new = {'RE': value_new}

        if isinstance(value_old, dict):
            for year in value_old:
                value_old[year] = convertValue(value_old[year])[0]
        else:
            tmp = convertValue(value_old)[0]
            value_old = {2025: tmp, 2050: tmp}

        for year in value_old:
            if year not in [2025, 2050]:
                value_new[year] = value_new[2025] + (value_new[2050]-value_new[2025])*(value_old[year]-value_old[2025])/(value_old[2050]-value_old[2025])

        __updateParameter(scenarioInput['params'][entry['name']], {'value': value_new})
        scenarioInput['params'][entry['name']]['type'] = 'linear'

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
def updateScenarioInputAdvanced(scenarioInput: dict, advanced_gwp: str, advanced_times: list, advanced_fuels: list, advanced_params: list):
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
