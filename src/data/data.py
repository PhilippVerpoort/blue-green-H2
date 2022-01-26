import pandas as pd

from src.config_load import units
from src.filepaths import getFilePath
from src.data.params.full_params import getFullParams
from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.data.fuels.calc_fuels import calcFuelData


# obtain all required data for a scenario
def getFullData(scenario: dict, export_data: bool = True):
    options, params, fuels = (scenario['options'], scenario['params'], scenario['fuels'])

    # convert basic inputs to complete dataframes
    fullParams = getFullParams(params, units, options['times'])

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

    return fuelSpecs, fuelData, FSCPData, fullParams


