import re
from typing import Union

import pandas as pd
import yaml

from src.filepaths import getFilePathInput, getFilePath
from src.data.calc_FSCPs import calcFSCPs
from src.data.calc_fuels import calcFuelData


# obtain all required data for a scenario
def obtainScenarioData(scenario: dict, export_data: bool = True):
    options, params, fuels = (scenario['options'], scenario['params'], scenario['fuels'])

    # load from yaml files
    units = __loadDataFromFiles()

    # convert basic inputs to complete dataframes
    fullParams = __getFullParams(params, units, options['times'])

    # calculate fuel data
    fuelData, fuelSpecs = calcFuelData(options['times'], fullParams, fuels, options['gwp'])

    # calculate FSCPs
    FSCPData = calcFSCPs(fuelData)

    # dump to output file
    if export_data:
        filePath = getFilePath('output/', 'data.xlsx')
        writer = pd.ExcelWriter(filePath)

        columnOrder = ['description', 'type', 'value', 'unit', 'source']

        pd.DataFrame(params).T.reindex(columnOrder, axis=1).to_excel(writer, sheet_name='Parameters (input)')
        pd.DataFrame(fuels).T.to_excel(writer, sheet_name='Fuel list (input)')

        fullParams.to_excel(writer, sheet_name='Parameters (full)')
        fuelData.to_excel(writer, sheet_name='Fuel data (output)')

        writer.save()

    return fuelData, fuelSpecs, FSCPData, fullParams


# load data from yaml files
def __loadDataFromFiles():
    filePath = getFilePathInput('data/units.yml')
    yamlData = yaml.load(open(filePath, 'r').read(), Loader=yaml.FullLoader)
    units = yamlData['units']

    return units


# calculate parameters at different times (using linear interpolation if needed)
def __getFullParams(basicData: dict, units: dict, times: list):
    fullDataFrame = pd.DataFrame(columns=['name', 'year', 'unit', 'value', 'uncertainty', 'uncertainty_lower'])

    for parId, par in basicData.items():
        newPars = __calcValues(parId, par['value'], par['type'], times)
        for newPar in newPars:
            if 'unit' in par and par['unit'] is not None:
                conversionFactor, newUnit = __convertUnit(par['unit'], units)
                newPar['value'] = conversionFactor * newPar['value']
                newPar['uncertainty'] = conversionFactor * newPar['uncertainty'] if newPar['uncertainty'] is not None else None
                newPar['uncertainty_lower'] = conversionFactor * newPar['uncertainty_lower'] if newPar['uncertainty_lower'] is not None else None
                newPar['unit'] = newUnit
            fullDataFrame = fullDataFrame.append(newPar, ignore_index=True)

    return fullDataFrame


# calculate values for different times and other keys from dict
def __calcValues(id:str, value: Union[dict, str, float], type: str, times: list):
    rs = []

    if isinstance(value, dict) and isinstance(list(value.keys())[0], str):
        for key, val in value.items():
            rs.extend(__calcValues(id+'_'+key, val, type, times))
        return rs

    if type == 'const':
        if not (isinstance(value, float) or isinstance(value, int) or isinstance(value, str)):
            raise Exception('Unknown type of value variable. Must be string (including uncertainty) or float.')

        value, uncertainty, uncertainty_lower = __convertValue(value)

        for t in times:
            r = {'name': id, 'year': t, 'value': value, 'uncertainty': uncertainty, 'uncertainty_lower': uncertainty_lower}
            rs.append(r)

    elif type == 'linear':
        if not isinstance(value, dict):
            raise Exception(f"Value must be a dict for type linear: {value}")

        if not all(isinstance(v, float) or isinstance(v, int) or isinstance(v, str) for v in value.values()):
            raise Exception('Unknown type of value variable. Must be string (including uncertainty) or float.')

        points = []
        for key, val in value.items():
            value, uncertainty, uncertainty_lower = __convertValue(val)
            points.append((key, value, uncertainty, uncertainty_lower))

        for t in times:
            value, uncertainty, uncertainty_lower = __linearInterpolate(t, points)
            r = {'name': id, 'year': t, 'value': value, 'uncertainty': uncertainty, 'uncertainty_lower': uncertainty_lower}
            rs.append(r)

    else:
        raise Exception("Unknown data type {}.".format(type))

    return rs


# convert string to floats with uncertainty
def __convertValue(value: Union[str, float, int]):
    if isinstance(value, float) or isinstance(value, int):
        return value, None, None
    elif isinstance(value, str):
        if ' +- ' in value:
            nums = value.split(' +- ')
            value = float(nums[0])
            uncertainty = float(nums[1])
            return value, uncertainty, None
        elif ' + ' in value and ' - ' in value:
            nums = re.split(r" [+-] ", value)
            value = float(nums[0])
            uncertainty = float(nums[1])
            uncertainty_lower = float(nums[2])
            return value, uncertainty, uncertainty_lower
        else:
            raise Exception('Incorrect syntax for uncertainty.')
    else:
        raise Exception('Unknown type of value variable.')



# convert units
def __convertUnit(unit: str, units: dict):
    for unitType, unitOptions in units['types'].items():
        if unit in unitOptions:
            newUnit = unitOptions[0]
            if unit == newUnit:
                return 1.0, unit
            else:
                return units['conversion'][f"{unit}__to__{newUnit}"], newUnit

    raise Exception(f"Unit not found: {unit}")


# linear interpolations
def __linearInterpolate(t: int, points: list):
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
