from src.proc_func.params import convert_unit
from src.utils import load_yaml_data_file, load_csv_data_file


def load_inputs(inputs: dict):
    # load input data from yaml files
    for key in ('options', 'params', 'fuels', 'units'):
        inputs[key] = load_yaml_data_file(key)

    # get options for each parameter
    inputs['params_options'] = {
        par_key: par_specs['options'] if 'options' in par_specs else []
        for par_key, par_specs in inputs['params'].items()
    }

    # load IEA CSV data into dataframe
    inputs['iea_data'] = load_csv_data_file('iea')
    inputs['iea_data'][['value', 'unit']] = inputs['iea_data'].apply(
        lambda row: convert_unit(row['reported_unit'], inputs['units'], row['reported_value']),
        axis=1,
        result_type='expand',
    )
