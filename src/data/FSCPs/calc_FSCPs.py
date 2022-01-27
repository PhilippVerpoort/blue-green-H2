import pandas as pd


def calcFSCPs(fuelData: pd.DataFrame):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   assign(fscp=lambda f: (f['cost_x'] - f['cost_y'])/(f['ghgi_y'] - f['ghgi_x'])).\
                   dropna()

    tmp['fscp_tc'] = tmp['cost_x'] + tmp['fscp'] * tmp['ghgi_x']

    tmp['correlated'] = 0.0
    tmp.loc[(tmp['type_x'] != 'green') & (tmp['type_y'] != 'green'), 'correlated'] = 1.0

    for i in ['uu', 'ul']:
        j = 'ul' if i == 'uu' else 'uu'
        tmp[f"fscp_{i}"] = (1.0 / (tmp['ghgi_y'] - tmp['ghgi_x'])) * (tmp[f"cost_{i}_x"] + tmp[f"cost_{j}_y"])

        ghgi_diff_u = tmp[f"ghgi_{i}_y"] + (1.0-tmp['correlated'])*tmp[f"ghgi_{j}_x"] - tmp['correlated']*tmp[f"ghgi_{i}_x"]

        tmp[f"fscp_{i}"] += (tmp['cost_x'] - tmp['cost_y']) / (tmp['ghgi_y'] - tmp['ghgi_x']) ** 2 * ghgi_diff_u

    FSCPData = tmp[['fuel_x', 'year_x', 'fuel_y', 'year_y', 'fscp', 'fscp_uu', 'fscp_ul', 'fscp_tc',
                    'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y']]

    return FSCPData
