known_tech_types = ['smr', 'smr-ccs-55%', 'atr-ccs-93%']
known_elec_srcs = ['RE', 'mix', 'share']


def calcGHGI(params: dict, fuel: dict, gwp: str):
    if fuel['type'] == 'ng':
        p = getGHGIParamsNG(*params, fuel, gwp)
        return getGHGING(**p)
    elif fuel['type'] == 'blue':
        p = getGHGIParamsBlue(*params, fuel, gwp)
        return getGHGIBlue(**p)
    elif fuel['type'] == 'green':
        p = getGHGIParamsGreen(*params, fuel, gwp)
        return getGHGIGreen(**p)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getGHGIParamsNG(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    return dict(
        b=(
            par[f"ghgi_ng_base_{GWP}"],
            par_uu[f"ghgi_ng_base_{GWP}"],
            par_ul[f"ghgi_ng_base_{GWP}"],
        ),
        mlr=(
            par['ghgi_ng_methaneleakage'],
            par_uu['ghgi_ng_methaneleakage'],
            par_ul['ghgi_ng_methaneleakage'],
        ),
        mghgi=par[f"ghgi_ng_methaneleakage_perrate_{GWP}"],
    )


def getGHGING(b, mlr, mghgi):

    return {
        'base': b,
        'mleakage': tuple(e*mghgi for e in mlr)
    }


def getGHGIParamsBlue(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception("Blue capture rate type unknown: {}".format(tech_type))

    return dict(
        b=(
            par[f"ghgi_blue_base_{tech_type}_{GWP}"],
            par_uu[f"ghgi_blue_base_{tech_type}_{GWP}"],
            par_ul[f"ghgi_blue_base_{tech_type}_{GWP}"],
        ),
        mlr=(
            par['ghgi_ng_methaneleakage'],
            par_uu['ghgi_ng_methaneleakage'],
            par_ul['ghgi_ng_methaneleakage'],
        ),
        mghgi=par[f"ghgi_blue_methaneleakage_perrate_{tech_type}_{GWP}"],
    )


def getGHGIBlue(b, mlr, mghgi):

    return {
        'base': b,
        'mleakage': tuple(e*mghgi for e in mlr)
    }


def getGHGIParamsGreen(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
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
        eghgi = (
           sum(shareof[tech_type]*par[f"ghgi_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_uu[f"ghgi_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_ul[f"ghgi_green_elec_{tech_type}_{GWP}"] for tech_type in ['RE', 'mix']),
        )
    else:
        eghgi = (
            par[f"ghgi_green_elec_{tech_type}_{GWP}"],
            par_uu[f"ghgi_green_elec_{tech_type}_{GWP}"],
            par_ul[f"ghgi_green_elec_{tech_type}_{GWP}"],
        )

    return dict(
        b=(
            par[f"ghgi_green_base_{GWP}"],
            par_uu[f"ghgi_green_base_{GWP}"],
            par_ul[f"ghgi_green_base_{GWP}"],
        ),
        eff=par[f"green_eff"],
        eghgi=eghgi,
    )


def getGHGIGreen(b, eff, eghgi):
    return {
        'base': b,
        'elec': tuple(e/eff for e in eghgi)
    }
