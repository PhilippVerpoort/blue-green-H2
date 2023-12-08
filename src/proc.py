from src.proc_func.fuels import calc_fuel_data
from src.proc_func.params import get_full_params


# process inputs into outputs
def process_inputs(inputs: dict, outputs: dict):
    options, params, params_options, fuels, units = (inputs['options'], inputs['params'], inputs['params_options'],
                                                     inputs['fuels'], inputs['units'])
    times, gwp = options['times'], options['gwp']

    # convert basic inputs to complete dataframes
    print('Getting full list of parameters...')
    full_params = get_full_params(params, units, times)

    # calculate fuel data
    print('Calculating fuel cost and GHGI data...')
    fuel_data, fuel_specs = calc_fuel_data(times, full_params, fuels, params, gwp, params_options, units)

    # return all output data
    outputs |= {
        'fullParams': full_params,
        'fuelSpecs': fuel_specs,
        'fuelData': fuel_data,
    }
