import pandas as pd

from src.config_load import units
from src.filepaths import getFilePath
from src.data.params.full_params import getFullParams
from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.data.fuels.calc_fuels import calcFuelData
from src.data.steel.calc_steel import calcSteelData


# obtain all required data for a scenario
def getFullData(input_data: dict, steel_data: dict, export_data: bool = True):
    options, params, fuels = (input_data['options'], input_data['params'], input_data['fuels'])

    # convert basic inputs to complete dataframes
    fullParams = getFullParams(params, units, options['times'])

    # calculate fuel data
    fuelData, fuelSpecs = calcFuelData(options['times'], fullParams, fuels, options['gwp'])

    # calculate steel data
    fuelDataSteel = calcSteelData(fuelData, steel_data)

    # calculate FSCPs
    FSCPData = calcFSCPs(fuelData)
    FSCPDataSteel = calcFSCPs(fuelDataSteel)

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

    return fullParams, fuelSpecs, fuelData, FSCPData, fuelDataSteel, FSCPDataSteel


