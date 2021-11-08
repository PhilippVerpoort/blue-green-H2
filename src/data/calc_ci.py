def calcCI(params: dict, coeffs: dict, fuel: dict, consts: dict, gwp: str):
    if fuel['type'] == 'ng':
        return __calcNG(params, consts, coeffs, fuel, gwp)
    elif fuel['type'] == 'blue':
        return __calcBlue(params, consts, coeffs, fuel, gwp)
    elif fuel['type'] == 'green':
        return __calcGreen(params, consts, coeffs, fuel, gwp)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def __calcNG(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    r = par[f"ci_ng_base_{GWP}"] + fuel['methane_leakage'] * par[f"ci_ng_methaneleakage_{GWP}"]

    return (r, 0.05*r)


def __calcBlue(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    CR = fuel['capture_rate']

    r = par[f"ci_blue_base_{CR}_{GWP}"] + fuel['methane_leakage'] * par[f"ci_blue_methaneleakage_{CR}_{GWP}"]

    return (r, 0.05*r)


def __calcGreen(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    ES = fuel['elecsrc']
    if ES not in ['re', 'mix']: raise Exception(f"Unknown elecsrc type: {ES}")

    r = par[f"ci_green_base_{GWP}"] + par[f"ci_green_eff"] * par[f"ci_green_elec_{ES}_{GWP}"]

    return (r, 0.05*r)
