known_ESs = ['hydro', 'wind', 'solar', 'custom', 'mix']


def calcCI(params: dict, coeffs: dict, fuel: dict, consts: dict, gwp: str):
    if fuel['type'] == 'ng':
        return getCING(params, consts, coeffs, fuel, gwp)
    elif fuel['type'] == 'blue':
        return getCIBlue(params, consts, coeffs, fuel, gwp)
    elif fuel['type'] == 'green':
        return getCIGreen(params, consts, coeffs, fuel, gwp)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getCING(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    return {
        'base': (par[f"ci_ng_base_{GWP}"], 0.05*par[f"ci_ng_base_{GWP}"]),
        'mleakage': (fuel['methane_leakage'] * par[f"ci_ng_methaneleakage_{GWP}"], 0.05 * fuel['methane_leakage'] * par[f"ci_ng_methaneleakage_{GWP}"])
    }


def getCIBlue(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    CR = fuel['capture_rate']

    return {
        'base': (par[f"ci_blue_base_{CR}_{GWP}"], 0.05*par[f"ci_blue_base_{CR}_{GWP}"]),
        'mleakage': (fuel['methane_leakage'] * par[f"ci_blue_methaneleakage_{CR}_{GWP}"], 0.05 * fuel['methane_leakage'] * par[f"ci_blue_methaneleakage_{CR}_{GWP}"])
    }


def getCIGreen(par: dict, const: dict, coef: dict, fuel: dict, GWP: str):
    ES = fuel['elecsrc']
    if ES not in known_ESs: raise Exception(f"Unknown elecsrc type: {ES}")

    return {
        'base': (par[f"ci_green_base_{GWP}"], 0.05*par[f"ci_green_base_{GWP}"]),
        'elec': (par[f"ci_green_eff"] * par[f"ci_green_elec_{ES}_{GWP}"], 0.05 * par[f"ci_green_eff"] * par[f"ci_green_elec_{ES}_{GWP}"])
    }
