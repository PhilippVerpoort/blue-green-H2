import numpy as np


def calcFSCPs(fuelData):
    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y')).\
                   assign(fscp=lambda f: (f['cost_x'] - f['cost_y'])/(f['ci_y'] - f['ci_x'])).\
                   dropna()

    tmp['fscp_tc'] = tmp['cost_x'] + tmp['fscp'] * tmp['ci_x']
    tmp['fscp_uu'] = np.sqrt(  (1.0/(tmp['ci_y'] - tmp['ci_x']) * tmp['cost_uu_x'])**2 +
                            (1.0/(tmp['ci_y'] - tmp['ci_x']) * tmp['cost_uu_y'])**2 +
                            ((tmp['cost_x'] - tmp['cost_y'])/(tmp['ci_y'] - tmp['ci_x'])**2 * tmp['ci_uu_y'])**2 +
                            ((tmp['cost_x'] - tmp['cost_y'])/(tmp['ci_y'] - tmp['ci_x'])**2 * tmp['ci_uu_x'])**2  )
    tmp['fscp_ul'] = np.sqrt(  (1.0/(tmp['ci_y'] - tmp['ci_x']) * tmp['cost_ul_x'])**2 +
                            (1.0/(tmp['ci_y'] - tmp['ci_x']) * tmp['cost_ul_y'])**2 +
                            ((tmp['cost_x'] - tmp['cost_y'])/(tmp['ci_y'] - tmp['ci_x'])**2 * tmp['ci_ul_y'])**2 +
                            ((tmp['cost_x'] - tmp['cost_y'])/(tmp['ci_y'] - tmp['ci_x'])**2 * tmp['ci_ul_x'])**2  )

    FSCPData = tmp[['fuel_x', 'year_x', 'fuel_y', 'year_y', 'fscp', 'fscp_uu', 'fscp_ul', 'fscp_tc']]

    return FSCPData
