import pandas as pd
import yaml

from src.calc_FSCPs import calcFSCPs
from src.calc_fuels import calcFuelData


# obtain all required data for a scenario
def obtainScenarioData(times: list):
    # load from yaml files
    params, coeffs, fuels, consts = __loadDataFromFiles()

    # convert basic inputs to complete dataframes
    fullParams = __getFullParamsCoeffs(params, times)
    fullCoeffs = __getFullParamsCoeffs(coeffs, times)

    # calculate fuel data
    fuelData = calcFuelData(fullParams, fullCoeffs, fuels, consts, times)

    # calculate FSCPs
    FSCPData = calcFSCPs(fuelData)

    # dump to output file
    with pd.ExcelWriter('output/data.xlsx') as writer:
        fullParams.to_excel(writer, sheet_name='Parameters')
        fullCoeffs.to_excel(writer, sheet_name='Coefficients')
        fuelData.to_excel(writer, sheet_name='Fuel Data')

    return fuelData, FSCPData


# load data from yaml files
def __loadDataFromFiles():
    yamlData = yaml.load(open('input/scenario_default.yml', 'r').read(), Loader=yaml.FullLoader)
    params = yamlData['params']
    fuels = yamlData['fuels']

    yamlData = yaml.load(open('input/coefficients.yml', 'r').read(), Loader=yaml.FullLoader)
    coeffs = yamlData['coeffs']

    yamlData = yaml.load(open('input/constants.yml', 'r').read(), Loader=yaml.FullLoader)
    consts = yamlData['constants']

    return params, coeffs, fuels, consts


# calculate parameters/coefficients based at different times (using linear interpolation if needed)
def __getFullParamsCoeffs(basicData: dict, times: list):
    fullDataFrame = pd.DataFrame(columns=['name', 'year', 'value', 'unit'])

    for par_id, par in basicData.items():
        if par['type'] == 'const':
            for t in times:
                new_par = {'name': par_id, 'year': t, 'value': par['value'], 'unit': par['unit']}
                fullDataFrame = fullDataFrame.append(new_par, ignore_index=True)
        elif par['type'] == 'linear':
            points = [(int(key.lstrip('value_')), par[key]) for key in par.keys() if key.startswith('value_')]
            points.sort(key=lambda x: x[0])

            for t in times:
                value = __linearInterpolate(t, points)
                new_par = {'name': par_id, 'year': t, 'value': value, 'unit': par['unit']}
                fullDataFrame = fullDataFrame.append(new_par, ignore_index=True)
        else:
            raise Exception("Unknown data type {}".format(par['type']))

    return fullDataFrame


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