import copy
from string import ascii_uppercase

import xlsxwriter

from src.filepaths import getFilePathOutput


def exportInputData(input_data: dict):
    options, params, fuels = (input_data['options'], input_data['params'], input_data['fuels'])

    # create XLSX file
    filePath = getFilePathOutput("parameter_table.xlsx")
    workbook = xlsxwriter.Workbook(filePath)

    # build worksheets
    __buildWorksheetParams(workbook, params)
    __buildWorksheetCases(workbook, params, fuels)

    # close and write workbook
    workbook.close()


def __buildWorksheetParams(workbook, params: dict):
    ws = workbook.add_worksheet('Base parameters')

    # add headers
    __addHeaders(workbook, ws, ['Parameter name', 'Unit', 'Type', 'Year', 'Value', 'Source'])

    # add parameter rows
    __addParamRows(ws, params, 0, 1)


# iterate over parameter keys, subkeys, and years
def __addParamRows(ws, params, startCol: int, paramStart: int):
    for paramKey, paramData in params.items():
        source = paramData['source'] if 'source' in paramData else ''
        options = paramData['options'] if 'options' in paramData else []

        if paramData['value'] == 'cases':
            continue

        typeStart = 0

        for entries in __getParams(paramData['value'], options, paramData['type']):
            typeEnd = typeStart + len(entries['values']) - 1

            optionsList = ', '.join([e.upper() for e in entries['options']])

            if len(entries['values']) > 1:
                ws.merge_range(__indexRange([paramStart + typeStart, paramStart + typeEnd], startCol+2), optionsList)
            else:
                ws.write(__index(paramStart + typeStart, startCol+2), optionsList)

            for k, year in enumerate(entries['values']):
                value = entries['values'][year]
                ws.write(__index(paramStart + typeStart + k, startCol+3), year)
                ws.write(__index(paramStart + typeStart + k, startCol+4), value)

            typeStart = typeEnd + 1

        paramEnd = paramStart + typeEnd

        # write parameter description, unit, and source
        if paramStart==paramEnd:
            ws.write(__index(paramStart, startCol + 0), paramData['desc'])
            ws.write(__index(paramStart, startCol + 1), paramData['unit'])
            ws.write(__index(paramStart, startCol + 5), source)
        else:
            ws.merge_range(__indexRange([paramStart, paramEnd], startCol+0), paramData['desc'])
            ws.merge_range(__indexRange([paramStart, paramEnd], startCol+1), paramData['unit'])
            ws.merge_range(__indexRange([paramStart, paramEnd], startCol+5), source)

        paramStart = paramEnd + 1

    return paramEnd


def __addHeaders(workbook, ws, cols: list):
    # add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # insert header row
    for colIndex, colName in enumerate(cols):
        ws.write(__index(0, colIndex), colName, bold)


def __buildWorksheetCases(workbook, params: dict, fuels: dict):
    ws = workbook.add_worksheet('Fuel-specific cases')

    # add parameter headers
    __addHeaders(workbook, ws, ['Fuel type', 'Case', 'Parameter name', 'Unit', 'Type', 'Year', 'Value', 'Source'])

    # loop over fuels and cases
    fuelStart = paramStart = 1
    for fuelID, fuelSpecs in fuels.items():
        # add cases
        for caseGroup in fuelSpecs['cases']:
            for caseName, caseDetails in fuelSpecs['cases'][caseGroup].items():
                # determine params of case
                paramsCase = {key: copy.deepcopy(params[key]) for key in caseDetails if key in params}
                if not paramsCase:
                    continue
                for pName in paramsCase:
                    paramsCase[pName]['value'] = caseDetails[pName]

                # add parameter rows
                paramEnd = __addParamRows(ws, paramsCase, 2, paramStart)

                # add case group and name
                ws.merge_range(__indexRange([paramStart, paramEnd], 1), f"{caseGroup} {caseName}")

                paramStart = paramEnd + 1

        # add fuel name
        ws.merge_range(__indexRange([fuelStart, paramEnd], 0), fuelID)
        fuelStart = paramEnd + 1


def __getParams(values, options: list, valtype: str):
    if options:
        return [
            {
                'options': [key] + e['options'],
                'values': e['values'],
            }
            for key, val in values.items() for e in __getParams(val, options[1:], valtype)
        ]
    elif valtype == 'linear' and isinstance(values, dict):
        return [{
            'options': [],
            'values': values,
        }]
    else:
        return [{
            'options': [],
            'values': {'const': values},
        }]


def __index(row: int, col: int):
    return f"{ascii_uppercase[col]}{row+1}"


def __indexRange(rows: list, col: int):
    return f"{ascii_uppercase[col]}{rows[0]+1}:{ascii_uppercase[col]}{rows[1]+1}"

