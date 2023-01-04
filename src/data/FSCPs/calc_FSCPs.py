import re

import pandas as pd

from src.timeit import timeit


@timeit
def calcFSCPs(fuelData: pd.DataFrame):
    fuelCrossData = fuelData.assign(code=lambda r: r.type.map({'NG': 0, 'BLUE': 1, 'GREEN': 2}))

    fuelCrossData = fuelCrossData.merge(fuelCrossData, on='year', how='outer', suffixes=('_x', '_y'))\
        .query(f"code_y < code_x")\
        .drop(columns=['code_x', 'code_y'])\
        .sort_values(by=['fuel_x', 'fuel_y', 'year'])\
        .reset_index(drop=True)

    return calcFSCPFromCostAndGHGI(fuelCrossData)


def calcFSCPFromCostAndGHGI(fuelCrossData: pd.DataFrame):
    # calc cost diff and ghgi diff
    fuelCrossData['cost_diff'] = fuelCrossData['cost_x'] - fuelCrossData['cost_y']
    fuelCrossData['ghgi_diff'] = fuelCrossData['ghgi_y'] - fuelCrossData['ghgi_x']

    # calc FSCPs from above diffs
    fuelCrossData['fscp'] = fuelCrossData['cost_diff'] / fuelCrossData['ghgi_diff']

    # find all parameters with uncertainty
    pat = re.compile(r"^(cost|ghgi)_(uu|ul)__(.*)_[xy]")
    pnames = []
    for componentColName in fuelCrossData.columns:
        m = pat.match(componentColName)
        if m is not None:
            pname = m.group(3)
            if pname not in pnames:
                pnames.append(pname)

    # compute upper and lower uncertainties
    uts = ['uu', 'ul']
    for ut in uts:
        uto = next(uto for uto in uts if uto != ut)

        for pname in pnames:
            newColName = f"fscp_{ut}__{pname}"
            fuelCrossData[newColName] = 0.0

            for mode in ['cost', 'ghgi']:
                for suffix in['x', 'y']:
                    utc = ut if suffix=='x' else uto
                    componentColName = f"{mode}_{utc}__{pname}_{suffix}"

                    if componentColName not in fuelCrossData.columns:
                        continue

                    fuelCrossData[newColName] += (+1 if suffix == 'x' else -1) * fuelCrossData[componentColName].fillna(0.0) / fuelCrossData[f"{mode}_diff"]

        fuelCrossData[f"fscp_{ut}"] = fuelCrossData['fscp'] * fuelCrossData[[f"fscp_{ut}__{pname}" for pname in pnames]].pow(2).sum(axis=1).pow(1/2)

    return fuelCrossData[[
        'year',
        'fuel_x', 'type_x', 'fuel_y', 'type_y',
        'cost_x', 'cost_y', 'cost_uu_x', 'cost_uu_y', 'cost_ul_x', 'cost_ul_y',
        'ghgi_x', 'ghgi_y', 'ghgi_uu_x', 'ghgi_uu_y', 'ghgi_ul_x', 'ghgi_ul_y',
        'fscp', 'fscp_uu', 'fscp_ul',
    ]]
