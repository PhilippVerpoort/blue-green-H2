known_ESs = ['hydro', 'wind', 'solar', 'custom', 'mix']


def calcCI(params: dict, fuel: dict, gwp: str):
    if fuel['type'] == 'ng':
        p = getCIParamsNG(params, fuel, gwp)
        return getCING(**p)
    elif fuel['type'] == 'blue':
        p = getCIParamsBlue(params, fuel, gwp)
        return getCIBlue(**p)
    elif fuel['type'] == 'green':
        p = getCIParamsGreen(params, fuel, gwp)
        return getCIGreen(**p)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getCIParamsNG(par: dict, fuel: dict, GWP: str):
    return dict(
        b=par[f"ci_ng_base_{GWP}"],
        mlr=fuel['methane_leakage'],
        mci=par[f"ci_ng_methaneleakage_{GWP}"],
    )


def getCING(b, mlr, mci):
    return {
        'base': (b,
                 b * 0.05),
        'mleakage': (mlr*mci,
                     mlr*mci * 0.05)
    }


def getCIParamsBlue(par: dict, fuel: dict, GWP: str):
    CR = fuel['capture_rate']

    return dict(
        b=par[f"ci_blue_base_{CR}_{GWP}"],
        mlr=fuel['methane_leakage'],
        mci=par[f"ci_blue_methaneleakage_{CR}_{GWP}"],
    )


def getCIBlue(b, mlr, mci):
    return {
        'base': (b,
                 b * 0.05),
        'mleakage': (mlr*mci,
                     mlr*mci * 0.05)
    }


def getCIParamsGreen(par: dict, fuel: dict, GWP: str):
    ES = fuel['elecsrc']
    if ES not in known_ESs: raise Exception(f"Unknown elecsrc type: {ES}")

    return dict(
        b=par[f"ci_green_base_{GWP}"],
        eff=par[f"ci_green_eff"],
        eci=par[f"ci_green_elec_{ES}_{GWP}"],
    )


def getCIGreen(b, eff, eci):
    return {
        'base': (b,
                 b * 0.05),
        'elec': (eff*eci,
                 eff*eci * 0.05),
    }
