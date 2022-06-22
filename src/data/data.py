import pandas as pd

from src.filepaths import getFilePathOutput
from src.data.params.full_params import getFullParams
from src.data.FSCPs.calc_FSCPs import calcFSCPs
from src.data.fuels.calc_fuels import calcFuelData
from src.data.steel.calc_steel import calcSteelData


# obtain all required data for a scenario
def getFullData(input_data: dict, steel_data: dict):
    options, params, fuels = (input_data['options'], input_data['params'], input_data['fuels'])

    # convert basic inputs to complete dataframes
    print('Getting full list of parameters...')
    fullParams = getFullParams(params, options['times'])

    # calculate fuel data
    print('Calculating fuel cost and GHGI data...')
    fuelData, fuelSpecs = calcFuelData(options['times'], fullParams, fuels, params, options['gwp'])

    # calculate steel data
    print('Calculating steel data...')
    fuelDataSteel = calcSteelData(fuelData, steel_data)

    # calculate FSCPs
    print('Calculating FSCPs...')
    FSCPData = calcFSCPs(fuelData)
    FSCPDataSteel = calcFSCPs(fuelDataSteel)

    # return all output data
    return {
        'fullParams': fullParams,
        'fuelSpecs': fuelSpecs,
        'fuelData': fuelData,
        'FSCPData': FSCPData,
        'fuelDataSteel': fuelDataSteel,
        'FSCPDataSteel': FSCPDataSteel,
    }


# export selected data into XLS output file
def exportDataXLS(input_data, output_data):
    print('Exporting to spreadsheet...')

    options, params, fuels = (input_data['options'], input_data['params'], input_data['fuels'])
    fullParams, fuelData = (output_data['fullParams'], output_data['fuelData'])

    filePath = getFilePathOutput('data.xlsx')
    writer = pd.ExcelWriter(filePath)

    columnOrder = ['description', 'type', 'value', 'unit', 'source']

    pd.DataFrame(params).T.reindex(columnOrder, axis=1).to_excel(writer, sheet_name='Parameters (input)')
    pd.DataFrame(fuels).T.to_excel(writer, sheet_name='Fuel list (input)')

    fullParams.to_excel(writer, sheet_name='Parameters (full)')
    fuelData.to_excel(writer, sheet_name='Fuel data (output)')

    writer.save()
