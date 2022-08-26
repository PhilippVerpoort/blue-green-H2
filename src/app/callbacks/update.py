import re
from typing import Union

import yaml
from dash.exceptions import PreventUpdate

from src.app.callbacks.simple_params import cons_vs_prog_params, gas_prices_params, editTablesModal
from src.data.params.full_params import convertValue


# simple update
def updateScenarioInput(scenarioInput: dict, simple_gwp: str, simple_important_params: list, simple_gas_prices: list, advanced_params: dict):
    # update gwp option
    scenarioInput['options']['gwp'] = simple_gwp

    for casesType, paramList, tableName, data in [('cons_vs_prog', cons_vs_prog_params, 'simple-important-params', simple_important_params),
                                                  ('gas_prices', gas_prices_params, 'simple-gas-prices', simple_gas_prices)]:
        for param, fuels in paramList.items():
            for fuel in fuels:
                for caseName in editTablesModal[tableName]:
                    row = next(i for i in range(len(data)) if data[i]['name']==param)
                    scenarioInput['fuels'][fuel]['cases'][casesType][caseName][param] = yaml.load(data[row][caseName], Loader=yaml.FullLoader)

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
