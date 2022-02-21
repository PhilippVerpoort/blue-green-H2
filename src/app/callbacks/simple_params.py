from typing import Union

from src.config_load import input_data
from src.data.params.full_params import convertValue

simpleParams = ['cost_green_capex', 'cost_green_elec', 'green_share',
                'green_ocf', 'ghgi_ng_methaneleakage', 'cost_h2transp']


def getSimpleParamsTable():
    r = []

    subtypes = {
        'cost_green_elec': ['RE'],
    }

    paramData = input_data['params']
    for parName in simpleParams:
        r.append({
            'name': parName,
            'desc': paramData[parName]['short'] if 'short' in paramData[parName] else paramData[parName]['desc'],
            'unit': paramData[parName]['unit'],
            'val_2025': __getParamValue(paramData[parName]['value'], 2025, subtypes[parName] if parName in subtypes else []),
            'val_2050': __getParamValue(paramData[parName]['value'], 2050, subtypes[parName] if parName in subtypes else []),
        })

    return r


def __getParamValue(value: Union[dict, float], year: int, subtypes: list = []):
    if subtypes:
        return __getParamValue(value[subtypes[0]], year, subtypes[1:])

    if isinstance(value, dict):
        return convertValue(value[year])[0]
    else:
        return convertValue(value)[0]

