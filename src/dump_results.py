from pathlib import Path

import pandas as pd


def dump_results(input_data: dict, output_data: dict, file_path: Path):
    # extract dataframes from inputs and outputs
    options, params, fuels = (input_data['options'], input_data['params'], input_data['fuels'])
    full_params, fuel_data = (output_data['fullParams'], output_data['fuelData'])

    # define ordering of columns
    column_order = ['description', 'type', 'value', 'unit', 'source']

    # create a writer object for an Excel spreadsheet
    with pd.ExcelWriter(file_path) as writer:
        pd.DataFrame(params).T.reindex(column_order, axis=1).to_excel(writer, sheet_name='Parameters (input)')
        pd.DataFrame(fuels).T.to_excel(writer, sheet_name='Fuel list (input)')

        full_params.to_excel(writer, sheet_name='Parameters (full)')
        fuel_data.to_excel(writer, sheet_name='Fuel data (output)')
