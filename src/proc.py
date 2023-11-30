# process cases
from src.data.fuels.calc_fuels import calcFuelData
from src.data.params.full_params import getFullParams


def process_inputs(inputs: dict, outputs: dict):
    options, params, params_options, fuels, units = inputs['options'], inputs['params'], inputs['params_options'], inputs['fuels'], inputs['units']
    times, gwp = options['times'], options['gwp']

    # convert basic inputs to complete dataframes
    print('Getting full list of parameters...')
    fullParams = getFullParams(params, units, times)

    # calculate fuel data
    print('Calculating fuel cost and GHGI data...')
    fuelData, fuelSpecs = calcFuelData(times, fullParams, fuels, params, gwp, params_options, units)

    # return all output data
    outputs |= {
        'fullParams': fullParams,
        'fuelSpecs': fuelSpecs,
        'fuelData': fuelData,
    }
