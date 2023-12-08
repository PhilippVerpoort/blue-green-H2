import copy
from pathlib import Path
from string import ascii_uppercase

import xlsxwriter


def dump_params(inputs: dict, file_path: Path):
    params, fuels = inputs['params'], inputs['fuels']

    # create XLSX file
    print('Exporting parameters to spreadsheet...')
    workbook = xlsxwriter.Workbook(file_path)

    # build worksheets
    _build_worksheet_params(workbook, params)
    _build_worksheet_cases(workbook, params, fuels)

    # close and write workbook
    workbook.close()
    print('Done!')


def _build_worksheet_params(workbook, params: dict):
    ws = workbook.add_worksheet('Base parameters')

    # add headers
    _add_headers(workbook, ws, ['Parameter name', 'Unit', 'Type', 'Year', 'Value', 'Source'])

    # add parameter rows
    _add_param_rows(ws, params, 0, 1)


# iterate over parameter keys, subkeys, and years
def _add_param_rows(ws, params, start_col: int, param_start: int):
    for param_key, param_data in params.items():
        source = param_data['source'] if 'source' in param_data else ''
        options = param_data['options'] if 'options' in param_data else []

        if param_data['value'] == 'cases':
            continue

        type_start = 0

        for entries in _get_params(param_data['value'], options, param_data['type']):
            type_end = type_start + len(entries['values']) - 1

            options_list = ', '.join([e.upper() for e in entries['options']])

            if len(entries['values']) > 1:
                ws.merge_range(_index_range(
                    [param_start + type_start, param_start + type_end], start_col + 2),
                    options_list,
                )
            else:
                ws.write(
                    _index(param_start + type_start, start_col + 2),
                    options_list,
                )

            for k, year in enumerate(entries['values']):
                value = entries['values'][year]
                ws.write(_index(param_start + type_start + k, start_col + 3), year)
                ws.write(_index(param_start + type_start + k, start_col + 4), value)

            type_start = type_end + 1

        param_end = param_start + type_end

        # write parameter description, unit, and source
        if param_start == param_end:
            ws.write(_index(param_start, start_col + 0), param_data['desc'])
            ws.write(_index(param_start, start_col + 1), param_data['unit'])
            ws.write(_index(param_start, start_col + 5), source)
        else:
            ws.merge_range(_index_range([param_start, param_end], start_col + 0), param_data['desc'])
            ws.merge_range(_index_range([param_start, param_end], start_col + 1), param_data['unit'])
            ws.merge_range(_index_range([param_start, param_end], start_col + 5), source)

        param_start = param_end + 1

    return param_end


def _add_headers(workbook, ws, cols: list):
    # add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # insert header row
    for colIndex, colName in enumerate(cols):
        ws.write(_index(0, colIndex), colName, bold)


def _build_worksheet_cases(workbook, params: dict, fuels: dict):
    ws = workbook.add_worksheet('Fuel-specific cases')

    # add parameter headers
    _add_headers(workbook, ws, ['Fuel type', 'Case', 'Parameter name', 'Unit', 'Type', 'Year', 'Value', 'Source'])

    # loop over fuels and cases
    fuel_start = param_start = 1
    for fuel_id, fuel_specs in fuels.items():
        # add cases
        for caseGroup in fuel_specs['cases']:
            for caseName, caseDetails in fuel_specs['cases'][caseGroup].items():
                # determine params of case
                params_case = {key: copy.deepcopy(params[key]) for key in caseDetails if key in params}
                if not params_case:
                    continue
                for pName in params_case:
                    params_case[pName]['value'] = caseDetails[pName]

                # add parameter rows
                param_end = _add_param_rows(ws, params_case, 2, param_start)

                # add case group and name
                ws.merge_range(_index_range([param_start, param_end], 1), f"{caseGroup} {caseName}")

                param_start = param_end + 1

        # add fuel name
        ws.merge_range(_index_range([fuel_start, param_end], 0), fuel_id)
        fuel_start = param_end + 1


def _get_params(values, options: list, valtype: str) -> list:
    if options:
        return [
            {
                'options': [key] + e['options'],
                'values': e['values'],
            }
            for key, val in values.items() for e in _get_params(val, options[1:], valtype)
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


def _index(row: int, col: int) -> str:
    return f"{ascii_uppercase[col]}{row+1}"


def _index_range(rows: list, col: int) -> str:
    return f"{ascii_uppercase[col]}{rows[0]+1}:{ascii_uppercase[col]}{rows[1]+1}"
