def calcCI(params: dict, coeffs: dict, fuel: dict, consts: dict):
    GWP = 'gwp20'

    if fuel['type'] == 'ng':
        return __calcNG(params, consts, coeffs, fuel, GWP)
    elif fuel['type'] == 'blue':
        return __calcBlue(params, consts, coeffs, fuel, GWP)
    elif fuel['type'] == 'green':
        return __calcGreen(params, consts, coeffs, fuel, GWP)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def __calcNG(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    r = par['ci_ng']

    return (r, 0.05*r)


def __calcBlue(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    CR = fuel['capture_rate']

    r = par[f"ci_blue_base_{CR}_{GWP}"] + fuel['methane_leakage'] * par[f"ci_blue_methaneleakage_{CR}_{GWP}"]

    return (r, 0.05*r)


def __calcGreen(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    # convert gCO2eq/MWh to tCO2eq/kWh
    if fuel['elecsrc'] == 'RE only':
        ET = 're'
    elif fuel['elecsrc'] == 'grid mix':
        ET = 'mix'
    else:
        raise Exception("Unknown elecsrc type!")

    r = par[f"ci_green_base_{GWP}"] + par[f"ci_green_eff"] * par[f"ci_green_elec_{ET}_{GWP}"]

    return (r, 0.05*r)
