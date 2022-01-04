known_tech_types = ['smr', 'smr+lcrccs', 'smr+hcrccs', 'atr+hcrccs']
known_elec_srcs = ['RE', 'mix']


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
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception("Blue capture rate type unknown: {}".format(tech_type))

    return dict(
        b=par[f"ci_blue_base_{tech_type}_{GWP}"],
        mlr=par['ci_ng_methaneleakage'],
        mci=par[f"ci_blue_methaneleakage_perrate_{tech_type}_{GWP}"],
    )


def getCIBlue(b, mlr, mci):
    return {
        'base': (b,
                 b * 0.05),
        'mleakage': (mlr*mci,
                     mlr*mci * 0.05)
    }


def getCIParamsGreen(par: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    return dict(
        b=par[f"ci_green_base_{GWP}"],
        eff=par[f"ci_green_eff"],
        eci=par[f"ci_green_elec_{tech_type}_{GWP}"],
    )


def getCIGreen(b, eff, eci):
    return {
        'base': (b,
                 b * 0.05),
        'elec': (eff*eci,
                 eff*eci * 0.05),
    }
