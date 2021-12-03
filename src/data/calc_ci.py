known_blue_types = ['smr', 'smr+lcrccs', 'smr+hcrccs', 'atr+hcrccs']
known_elec_srcs = ['hydro', 'wind', 'solar', 'custom', 'mix']


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
        mlr=par['ci_ng_methaneleakage'],
        mci=par[f"ci_ng_methaneleakage_perrate_{GWP}"],
    )


def getCING(b, mlr, mci):
    return {
        'base': (b,
                 b * 0.05),
        'mleakage': (mlr*mci,
                     mlr*mci * 0.05)
    }


def getCIParamsBlue(par: dict, fuel: dict, GWP: str):
    CR = fuel['blue_type']
    if CR not in known_blue_types:
        raise Exception("Blue capture rate type unknown: {}".format(CR))

    return dict(
        b=par[f"ci_blue_base_{CR}_{GWP}"],
        mlr=par['ci_ng_methaneleakage'],
        mci=par[f"ci_blue_methaneleakage_perrate_{CR}_{GWP}"],
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
    if ES not in known_elec_srcs: raise Exception(f"Unknown elecsrc type: {ES}")

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
