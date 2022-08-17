import numpy as np
import pandas as pd

from src.timeit import timeit


@timeit
def calcFSCPs(fuelData: pd.DataFrame):
    fuelData = fuelData.filter(['fuel', 'type', 'year', 'cost', 'cost_uu', 'cost_ul', 'ghgi', 'ghgi_uu', 'ghgi_ul']) \
                       .assign(code=lambda r: r.type.map({'NG': 0, 'BLUE': 1, 'GREEN': 2}))

    tmp = fuelData.merge(fuelData, how='cross', suffixes=('_x', '_y'))\
                  .query(f"code_x < code_y")\
                  .drop(columns=['code_x', 'code_y'])

    tmp['correlated'] = 0.0
    tmp.loc[(tmp['type_x'] != 'GREEN') & (tmp['type_y'] != 'GREEN'), 'correlated'] = 1.0

    fscp, fscpu = calcFSCPFromCostAndGHGI(
        tmp['cost_x'],
        tmp['ghgi_x'],
        tmp['cost_y'],
        tmp['ghgi_y'],
        [tmp[f"cost_{i}_x"] for i in ['uu', 'ul']],
        [tmp[f"ghgi_{i}_x"] for i in ['uu', 'ul']],
        [tmp[f"cost_{i}_y"] for i in ['uu', 'ul']],
        [tmp[f"ghgi_{i}_y"] for i in ['uu', 'ul']],
        corr=tmp['correlated'],
    )

    tmp['fscp'] = fscp
    tmp['fscp_uu'] = fscpu[0]
    tmp['fscp_ul'] = fscpu[1]

    tmp['fscp_tc'] = tmp['cost_x'] + tmp['fscp'] * tmp['ghgi_x']

    FSCPData = tmp[['fuel_x', 'type_x', 'year_x', 'fuel_y', 'type_y', 'year_y', 'fscp', 'fscp_uu', 'fscp_ul', 'fscp_tc',
                    'cost_x', 'cost_y', 'ghgi_x', 'ghgi_y', 'cost_uu_x', 'cost_uu_y', 'ghgi_uu_x', 'ghgi_uu_y', 'cost_ul_x',
                    'cost_ul_y', 'ghgi_ul_x', 'ghgi_ul_y']]

    return FSCPData


def calcFSCPFromCostAndGHGI(cx, gx, cy, gy, cxu, gxu, cyu, gyu, corr = 0.0):
    fscp = (cy - cx) / (gx - gy)

    fscpu = [0.0, 0.0]

    if all(l and len(l) == 2 for l in [cxu, gxu, cyu, gyu]):
        for i in range(2):
            j = 0 if i else 1

            fscpu[i] += np.sqrt((fscp / (cy-cx)) ** 2 * (cyu[i] ** 2 + cxu[j] ** 2 - corr * 2 * cyu[i] * cxu[j]))
            fscpu[i] += np.sqrt((fscp / (gx-gy)) ** 2 * (gyu[i] ** 2 + gxu[j] ** 2 - corr * 2 * gyu[i] * gxu[j]))

    return fscp, fscpu
