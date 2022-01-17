known_tech_types = ['smr', 'smr+lcrccs', 'smr+hcrccs', 'atr+hcrccs']
known_elec_srcs = ['RE', 'mix', 'share']


def calcCI(params: dict, fuel: dict, gwp: str):
    if fuel['type'] == 'ng':
        p = getCIParamsNG(*params, fuel, gwp)
        return getCING(**p)
    elif fuel['type'] == 'blue':
        p = getCIParamsBlue(*params, fuel, gwp)
        return getCIBlue(**p)
    elif fuel['type'] == 'green':
        p = getCIParamsGreen(*params, fuel, gwp)
        return getCIGreen(**p)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getCIParamsNG(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    return dict(
        b=(
            par[f"ci_ng_base_{GWP}"],
            par_uu[f"ci_ng_base_{GWP}"],
            par_ul[f"ci_ng_base_{GWP}"],
        ),
        mlr=(
            par['ci_ng_methaneleakage'],
            par_uu['ci_ng_methaneleakage'],
            par_ul['ci_ng_methaneleakage'],
        ),
        mci=par[f"ci_ng_methaneleakage_perrate_{GWP}"],
    )


def getCING(b, mlr, mci):

    return {
        'base': b,
        'mleakage': tuple(e*mci for e in mlr)
    }


def getCIParamsBlue(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception("Blue capture rate type unknown: {}".format(tech_type))

    return dict(
        b=(
            par[f"ci_blue_base_{tech_type}_{GWP}"],
            par_uu[f"ci_blue_base_{tech_type}_{GWP}"],
            par_ul[f"ci_blue_base_{tech_type}_{GWP}"],
        ),
        mlr=(
            par['ci_ng_methaneleakage'],
            par_uu['ci_ng_methaneleakage'],
            par_ul['ci_ng_methaneleakage'],
        ),
        mci=par[f"ci_blue_methaneleakage_perrate_{tech_type}_{GWP}"],
    )


def getCIBlue(b, mlr, mci):

    return {
        'base': b,
        'mleakage': tuple(e*mci for e in mlr)
    }


def getCIParamsGreen(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    sharemix = par['green_share']
    if tech_type == 'mix':
        sharemix = 1.0
    elif tech_type == 'RE':
        sharemix = 0.0
    shareof = {
        'RE': (1-sharemix),
        'mix': sharemix,
    }

    if tech_type == 'share':
        eci = (
           sum(shareof[tech_type]*par[f"ci_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_uu[f"ci_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_ul[f"ci_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
        )
    else:
        eci = (
            par[f"ci_green_elec_{tech_type}_{GWP}"],
            par_uu[f"ci_green_elec_{tech_type}_{GWP}"],
            par_ul[f"ci_green_elec_{tech_type}_{GWP}"],
        )

    return dict(
        b=(
            par[f"ci_green_base_{GWP}"],
            par_uu[f"ci_green_base_{GWP}"],
            par_ul[f"ci_green_base_{GWP}"],
        ),
        eff=par[f"green_eff"],
        eci=eci,
    )


def getCIGreen(b, eff, eci):
    return {
        'base': b,
        'elec': tuple(e/eff for e in eci)
    }
