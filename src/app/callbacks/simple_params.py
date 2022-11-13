from typing import Union

import yaml

from src.config_load import input_data
from src.data.params.full_params import convertValue


cons_vs_prog_params = {
    'ghgi_ng_methaneleakage': ['NG', 'BLUE'],
    'cost_green_elec': ['GREEN'],
    'cost_green_capex': ['GREEN'],
    'green_share': ['GREEN'],
    'green_ocf': ['GREEN'],
    'cost_h2transp': ['GREEN'],
}

gas_prices_params = {
    'cost_ng_price': ['NG', 'BLUE'],
}

editTablesModal = {
    'simple-important-params': ['cons', 'prog'],
    'simple-gas-prices': ['high', 'low'],
    'advanced-params': ['value'],
}


def getSimpleParamsTable(paramList: dict, casesNames: list, casesType: str):
    r = []

    paramData = input_data['params']
    for parName in paramList:
        fuel = paramList[parName][0]
        r.append({
            'name': parName,
            'desc': paramData[parName]['short'] if 'short' in paramData[parName] else paramData[parName]['desc'],
            'unit': paramData[parName]['unit'],
            **{
                case: yaml.dump(__getDefaultValue(parName, fuel, casesType, case))
                for case in casesNames
            },
        })

    return r


def __getDefaultValue(parName: str, fuel: str, casesType: str, case: str):
    fuelData = input_data['fuels']
    paramData = input_data['params']
    return fuelData[fuel]['cases'][casesType][case][parName] if parName in fuelData[fuel]['cases'][casesType][case] else paramData[parName]['value']
