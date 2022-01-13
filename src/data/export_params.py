import csv

from src.filepaths import getFilePathOutput


def exportScenarioParams(scenario: dict):
    params = []

    for key, val in scenario['params'].items():
        params.extend(__printScenarioValue(val['desc'], val['unit'], val['value']))

    __writeToFile(params, 'table_scenario_params.csv')


def __printScenarioValue(name, unit, value):
    if isinstance(value, dict) and isinstance(list(value.keys())[0], str):
        r = []
        for key, val in value.items():
            r.extend(__printScenarioValue(f"{name} {key}", unit, val))
        return r
    elif isinstance(value, dict):
        return [(name, unit, "{0}: {1}".format(*list(value.items())[0]), "{0}: {1}".format(*list(value.items())[-1]))]
    else:
        return [(name, unit, f"2025: {value}", f"2050: {value}")]


def exportFullParams(fullParams: dict):
    yearInit = 2025
    yearFinal = 2050

    fullParamsInit = fullParams.query(f"year == {yearInit}").drop(columns=['year'])
    fullParamsFinal = fullParams.query(f"year == {yearFinal}").drop(columns=['year'])

    fullParamInitFinal = fullParamsInit.merge(fullParamsFinal, on=['name', 'unit'], how='outer', suffixes=('_init', '_final'))

    params = []

    for index, row in fullParamInitFinal.iterrows():
        vi = __printValueFull(row['value_init'], row['uncertainty_init'], row['uncertainty_lower_init'])
        vf = __printValueFull(row['value_final'], row['uncertainty_final'], row['uncertainty_lower_final'])

        params.append((row['name'], row['unit'], vi, vf))

    __writeToFile(params, 'table_full_params.csv')


def __printValueFull(val, uu, ul):
    if uu is None:
        return f"{val}\t"
    elif ul is None:
        return f"{val} +- {uu}\t"
    else:
        return f"{val} + {uu} - {ul}\t"


def __writeToFile(params: list, fname: str):
    filePath = getFilePathOutput(fname)
    with open(filePath, 'w') as csvFile:
        spamwriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(params)
