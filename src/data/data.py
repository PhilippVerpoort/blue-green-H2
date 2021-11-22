import pandas as pd
import yaml

from src.data.calc_FSCPs import calcFSCPs
from src.data.calc_fuels import calcFuelData


# obtain all required data for a scenario
from src.filepaths import getFilePathInputs


def obtainScenarioData(scenario: dict, export_data = True):
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
        writer = pd.ExcelWriter('output/data.xlsx')

        columnOrder = ['description', 'type', 'value', 'unit', 'source']

        pd.DataFrame(params).T.reindex(columnOrder, axis=1).to_excel(writer, sheet_name='Parameters (input)')
        pd.DataFrame(fuels).T.to_excel(writer, sheet_name='Fuel list (input)')

        fullParams.to_excel(writer, sheet_name='Parameters (full)')
        fuelData.to_excel(writer, sheet_name='Fuel data (output)')

        writer.save()

    return fuelData, fuelSpecs, FSCPData, fullParams


# load data from yaml files
def __loadDataFromFiles():
    filePath = getFilePathInputs('data/units.yml')
    yamlData = yaml.load(open(filePath, 'r').read(), Loader=yaml.FullLoader)
    units = yamlData['units']

    return units


# calculate parameters/coefficients based at different times (using linear interpolation if needed)
def __getFullParams(basicData: dict, units: dict, times: list):
    fullDataFrame = pd.DataFrame(columns=['name', 'year', 'value', 'unit'])

    for parId, par in basicData.items():
        newPars = __calcValues(parId, par['value'], par['type'], times)
        for newPar in newPars:
            if 'unit' in par and par['unit'] is not None:
                val, unit = __convertUnit(newPar['value'], par['unit'], units)
                newPar['value'] = val
                newPar['unit'] = unit
            fullDataFrame = fullDataFrame.append(newPar, ignore_index=True)

    return fullDataFrame


# calculate values for different times and other keys from dict
def __calcValues(id:str, value, type: str, times: list):
    if type == 'const':
        if isinstance(value, dict):
            r = []
            for key, val in value.items():
                r.extend(__calcValues(id+'_'+key, val, type, times))
        else:
            r = [{'name': id, 'year': t, 'value': value} for t in times]
    elif type == 'linear':
        if not isinstance(value, dict):
            raise Exception(f"Value must be a dict for type linear: {value}")
        elif isinstance(list(value.keys())[0], str):
            r = []
            for key, val in value.items():
                r.extend(__calcValues(id+'_'+key, val, type, times))
        else:
            points = [(key, val) for key, val in value.items()]
            points.sort(key=lambda x: x[0])
            r = [{'name': id, 'year': t, 'value': __linearInterpolate(t, points)} for t in times]
    else:
        raise Exception("Unknown data type {}.".format(type))

    return r


# convert units
def __convertUnit(val: float, unit: str, units: dict):
    for unitType, unitOptions in units['types'].items():
        if unit in unitOptions:
            newUnit = unitOptions[0]
            if unit == newUnit:
                return val, unit
            else:
                return val * units['conversion'][f"{unit}__to__{newUnit}"], newUnit

    raise Exception(f"Unit not found: {unit}")


# linear interpolations
def __linearInterpolate(t: int, points: list):
    p_min = None
    p_max = None

    for t_p, val_p in points:
        if t_p == t:
            return val_p
        elif t_p < t:
            if p_min is None or t_p > max(p_min, key = lambda x: x[0]):
                p_min = (t_p, val_p)
        elif t_p > t:
            if p_max is None or t_p < max(p_max, key = lambda x: x[0]):
                p_max = (t_p, val_p)
        else:
            raise ValueError()

    if p_min is None: return p_max[2]
    if p_max is None: return p_min[2]
    if p_min is None and p_max is None: raise Exception("Not enough interpolation points!")

    (t1, val1) = p_min
    (t2, val2) = p_max

    return val1 + (val2-val1)/(t2-t1) * (t-t1)
