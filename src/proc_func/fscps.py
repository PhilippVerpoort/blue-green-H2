import re

import numpy as np
import pandas as pd


def calc_interpolate_selected_fscps(fuel_data: pd.DataFrame, selected_cases: dict, n_samples: int,
                                    calc_unc: bool = True) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    plot_scatter = {}
    plot_interpolation = {}

    for scid, fuels in selected_cases.items():
        # insert interpolation points
        t = np.linspace(fuel_data['year'].min(), fuel_data['year'].max(), n_samples)

        tmp = []
        for f in fuels:
            support = fuel_data \
                .query(f"fuel=='{f}'") \
                .reset_index(drop=True) \
                .astype({'year': float})

            interpolation = dict(
                year=t,
                fuel=n_samples * [f],
                type=n_samples * [support.type.iloc[0]],
            )

            tmp.append(
                pd.merge(
                    support,
                    pd.DataFrame(interpolation, columns=support.keys()),
                    on=['year', 'fuel', 'type'],
                    how='outer',
                    suffixes=('', '_drop'),
                )
                .sort_values(by=['year'])
                .reset_index(drop=True)
                .interpolate()
                .dropna(axis='columns')
            )

        fuel_data_interpolated = pd.concat(tmp)

        # compute FSCPs
        plot_interpolation[scid] = calc_fscps(fuel_data_interpolated, calc_unc) \
            .assign(tid=lambda r: r.fuel_y + ' to ' + r.fuel_x)
        years = fuel_data.year.unique()
        plot_scatter[scid] = plot_interpolation[scid].query(f"year in @years")

    return plot_scatter, plot_interpolation


def calc_fscps(fuel_data: pd.DataFrame, calc_unc: bool = True):
    fuel_data_cross = fuel_data.assign(code=lambda r: r.type.map({'NG': 0, 'BLUE': 1, 'GREEN': 2}))

    fuel_data_cross = fuel_data_cross.merge(fuel_data_cross, on='year', how='outer', suffixes=('_x', '_y'))\
        .query(f"code_y < code_x")\
        .drop(columns=['code_x', 'code_y'])\
        .sort_values(by=['fuel_x', 'fuel_y', 'year'])\
        .reset_index(drop=True)

    return calc_fscp_from_cost_and_ghgi(fuel_data_cross, calc_unc)


def calc_fscp_from_cost_and_ghgi(fuel_data_cross: pd.DataFrame, calc_unc: bool = True):
    # calc cost diff and ghgi diff
    fuel_data_cross['cost_diff'] = fuel_data_cross['cost_x'] - fuel_data_cross['cost_y']
    fuel_data_cross['ghgi_diff'] = fuel_data_cross['ghgi_y'] - fuel_data_cross['ghgi_x']

    # calc FSCPs from above diffs
    fuel_data_cross['fscp'] = fuel_data_cross['cost_diff'] / fuel_data_cross['ghgi_diff']

    # only proceed if uncertainty needs to be calculated
    if not calc_unc:
        return fuel_data_cross[[
            'year',
            'fuel_x', 'type_x', 'fuel_y', 'type_y',
            'cost_x', 'cost_y', 'cost_uu_x', 'cost_uu_y', 'cost_ul_x', 'cost_ul_y',
            'ghgi_x', 'ghgi_y', 'ghgi_uu_x', 'ghgi_uu_y', 'ghgi_ul_x', 'ghgi_ul_y',
            'fscp',
        ]]

    # find all parameters with uncertainty
    pat = re.compile(r"^(cost|ghgi)_(uu|ul)__(.*)_[xy]")
    pnames = []
    for component_col_name in fuel_data_cross.columns:
        m = pat.match(component_col_name)
        if m is not None:
            pname = m.group(3)
            if pname not in pnames:
                pnames.append(pname)

    # compute upper and lower uncertainties
    uts = ['uu', 'ul']
    for ut_this in uts:
        ut_other = next(uto for uto in uts if uto != ut_this)

        for pname in pnames:
            new_col_name = f"fscp_{ut_this}__{pname}"
            fuel_data_cross[new_col_name] = 0.0

            for mode in ['cost', 'ghgi']:
                for suffix in ['x', 'y']:
                    ut_comp = ut_this if suffix == 'x' else ut_other
                    component_col_name = f"{mode}_{ut_comp}__{pname}_{suffix}"

                    if component_col_name not in fuel_data_cross.columns:
                        continue

                    fuel_data_cross[new_col_name] += ((+1 if suffix == 'x' else -1) *
                                                      fuel_data_cross[component_col_name].fillna(0.0) /
                                                      fuel_data_cross[f"{mode}_diff"])

        fuel_data_cross[f"fscp_{ut_this}"] = (
                fuel_data_cross['fscp'] *
                fuel_data_cross[[f"fscp_{ut_this}__{pname}" for pname in pnames]].pow(2).sum(axis=1).pow(1 / 2)
        )

    return fuel_data_cross[[
        'year',
        'fuel_x', 'type_x', 'fuel_y', 'type_y',
        'cost_x', 'cost_y', 'cost_uu_x', 'cost_uu_y', 'cost_ul_x', 'cost_ul_y',
        'ghgi_x', 'ghgi_y', 'ghgi_uu_x', 'ghgi_uu_y', 'ghgi_ul_x', 'ghgi_ul_y',
        'fscp', 'fscp_uu', 'fscp_ul',
    ]]
