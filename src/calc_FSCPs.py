def calcFSCPs(fuelData):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   assign(fscp=lambda f: (f['cost_x'] - f['cost_y'])/(f['ci_y'] - f['ci_x']),
                          fscp_tc=lambda f: f['cost_x'] + f['fscp'] * f['ci_x']).\
                   dropna()

    FSCPData = tmp[['fuel_x', 'year_x', 'fuel_y', 'year_y', 'fscp', 'fscp_tc']]

    return FSCPData