import re
from typing import Union

import pandas as pd

from src.config_load import units
from src.timeit import timeit


# Calculate parameters including uncertainty at different times, using linear interpolation if needed.
def getFullParams(basicData: dict, times: list):
    pars = []

    for parId, par in basicData.items():
        if par['value'] == 'cases': continue

        newPars = __calcValues(parId, par['value'], par['type'], times)
        for newPar in newPars:
            # set relative uncertainty if not provided explicitly
            if newPar['unc_upper'] is None or newPar['unc_lower'] is None:
                if 'uncertainty' in par and par['uncertainty']:
                    if isinstance(par['uncertainty'], float):
                        unc_rel = par['uncertainty']
                    elif isinstance(par['uncertainty'], str) and re.match(r'([0-9]*\.?[0-9]*)\s*%', par['uncertainty']):
                        unc_rel = float(par['uncertainty'].rstrip('%'))/100.0
                    else:
                        raise Exception(f"Unknown relative uncertainty format: {par['uncertainty']}")
                    newPar['unc_upper'] = unc_rel * newPar['value']
                    newPar['unc_lower'] = unc_rel * newPar['value']

            # convert unit
            if 'unit' in par and par['unit'] is not None:
                conversionFactor, newUnit = convert_unit(par['unit'])

                newPar['value'] = conversionFactor * newPar['value']
                newPar['unc_upper'] = conversionFactor * newPar['unc_upper'] if newPar['unc_upper'] is not None else None
                newPar['unc_lower'] = conversionFactor * newPar['unc_lower'] if newPar['unc_lower'] is not None else None

                newPar['unit'] = newUnit

            pars.append(newPar)

    r = pd.DataFrame.from_records(pars, columns=['name', 'year', 'unit', 'value', 'unc_upper', 'unc_lower'])\
                    .set_index(['name', 'year'])\
                    .rename(columns={'value': 'val', 'unc_upper': 'uu', 'unc_lower': 'ul'})

    return r


# Iteratively calculate values for 1) keys (smr/atr, gwp100/gwp20, etc) and 2) different times (2025, 2030, 2035, etc).
def __calcValues(id:str, value: Union[dict, str, float], type: str, times: list):
    rs = []

    if isinstance(value, dict) and isinstance(list(value.keys())[0], str) and '+' not in list(value.keys())[0]:
        for key, val in value.items():
            rs.extend(__calcValues(id+'_'+key, val, type, times))
        return rs

    if type == 'const' or isinstance(value, float) or isinstance(value, int) or isinstance(value, str):
        if not (isinstance(value, float) or isinstance(value, int) or isinstance(value, str)):
            raise Exception('Unknown type of value variable. Must be string (including uncertainty) or float.')

        value, unc_upper, unc_lower = __convertValue(value)

        for t in times:
            r = {'name': id, 'year': t, 'value': value, 'unc_upper': unc_upper, 'unc_lower': unc_lower}
            rs.append(r)

    elif type == 'linear' and isinstance(value, dict):
        if not all(isinstance(v, float) or isinstance(v, int) or isinstance(v, str) for v in value.values()):
            raise Exception('Unknown type of value variable. Must be string (including uncertainty) or float.')

        points = []
        for key, val in value.items():
            value, unc_upper, unc_lower = __convertValue(val)
            points.append((key, value, unc_upper, unc_lower))

        for t in times:
            value, unc_upper, unc_lower = __linearInterpolate(t, points)
            r = {'name': id, 'year': t, 'value': value, 'unc_upper': unc_upper, 'unc_lower': unc_lower}
            rs.append(r)

    else:
        raise Exception(f"Unknown data type {format(type)}.")

    return rs


# Convert strings to floats with uncertainty, e.g. string '1.0 +- 0.1' becomes tuple (1.0, 0.1, 0.1).
def __convertValue(value: Union[str, float, int]):
    if isinstance(value, float) or isinstance(value, int):
        return value, None, None
    elif isinstance(value, str):
        if ' +- ' in value:
            nums = value.split(' +- ')

            if len(nums) != 2:
                raise Exception(f"Incorrect formatting of value: {value}")

            val = float(nums[0])
            unc = float(nums[1])
            return val, unc, unc
        elif ' + ' in value and ' - ' in value:
            nums = re.split(r' [+-] ', value)

            if len(nums) != 3:
                raise Exception(f"Incorrect formatting of value: {value}")

            val = float(nums[0])
            if value.index('+') < value.index('-'):
                unc_upper = float(nums[1])
                unc_lower = float(nums[2])
            else:
                unc_upper = float(nums[2])
                unc_lower = float(nums[1])
            return val, unc_upper, unc_lower
        else:
            raise Exception('Incorrect syntax for uncertainty.')
    else:
        raise Exception('Unknown type of value variable.')


# Convert all units to standard units for straightforward calculation later on.
def convert_unit(unit: str, value: float = 1.0):
    for unitType, unitOptions in units['types'].items():
        if unit in unitOptions:
            newUnit = unitOptions[0]
            if unit == newUnit:
                return value, unit
            else:
                return units['conversion'][f"{unit}__to__{newUnit}"] * value, newUnit

    raise Exception(f"Unit not found: {unit}")


# Select value provided for time t. Alternatively, if not existent, interpolate to time t from adjacent points.
def __linearInterpolate(t: int, points: list):
    if len(points) == 1:
        t, val, unc, uncl = points[0]
        return val, unc, uncl

    p_min = None
    p_max = None

    for t_p, val_p, unc_p, uncl_p in points:
        if t_p == t:
            return val_p, unc_p, uncl_p
        elif t_p < t:
            if p_min is None or t_p > p_min[0]:
                p_min = (t_p, val_p, unc_p, uncl_p)
        elif t_p > t:
            if p_max is None or t_p < p_max[0]:
                p_max = (t_p, val_p, unc_p, uncl_p)
        else:
            raise ValueError()

    if p_min is None: return p_max[2:4]
    if p_max is None: return p_min[2:4]
    if p_min is None and p_max is None: raise Exception("Not enough interpolation points!")

    (t1, val1, unc1, uncl1) = p_min
    (t2, val2, unc2, uncl2) = p_max

    # set lower uncertainty equal to upper uncertainty if not set for only one of the two points
    if uncl1 != uncl2 and None in [uncl1, uncl2]:
        uncl1 = unc1 if uncl1 is None else uncl1
        uncl2 = unc2 if uncl2 is None else uncl2

    val = val1 + (val2-val1)/(t2-t1) * (t-t1)
    unc = unc1 + (unc2-unc1)/(t2-t1) * (t-t1) if not (unc1 is None or unc2 is None) else None
    uncl = uncl1 + (uncl2-uncl1)/(t2-t1) * (t-t1) if not (uncl1 is None or uncl2 is None) else None

    return val, unc, uncl
