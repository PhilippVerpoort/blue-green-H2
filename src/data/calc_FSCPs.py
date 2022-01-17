def calcFSCPs(fuelData):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   assign(fscp=lambda f: (f['cost_x'] - f['cost_y'])/(f['ci_y'] - f['ci_x'])).\
                   dropna()

    tmp['fscp_tc'] = tmp['cost_x'] + tmp['fscp'] * tmp['ci_x']

    tmp['correlated'] = 0.0
    tmp.loc[(tmp['type_x'] != 'green') & (tmp['type_y'] != 'green'), 'correlated'] = 1.0

    for i in ['uu', 'ul']:
        j = 'ul' if i == 'uu' else 'uu'
        tmp[f"fscp_{i}"] = (1.0 / (tmp['ci_y'] - tmp['ci_x'])) * (tmp[f"cost_{i}_x"] + tmp[f"cost_{j}_y"])

        ci_diff_u = tmp[f"ci_{i}_y"] + (1.0-tmp['correlated'])*tmp[f"ci_{j}_x"] - tmp['correlated']*tmp[f"ci_{i}_x"]

        tmp[f"fscp_{i}"] += (tmp['cost_x'] - tmp['cost_y']) / (tmp['ci_y'] - tmp['ci_x']) ** 2 * ci_diff_u

    FSCPData = tmp[['fuel_x', 'year_x', 'fuel_y', 'year_y', 'fscp', 'fscp_uu', 'fscp_ul', 'fscp_tc']]

    return FSCPData
