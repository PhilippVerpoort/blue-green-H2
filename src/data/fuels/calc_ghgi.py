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
        bdir=(
            par[f"ghgi_ng_base_direct_{GWP}"],
            par_uu[f"ghgi_ng_base_direct_{GWP}"],
            par_ul[f"ghgi_ng_base_direct_{GWP}"],
        ),
        bele=(
            par[f"ghgi_ng_base_elec_{GWP}"],
            par_uu[f"ghgi_ng_base_elec_{GWP}"],
            par_ul[f"ghgi_ng_base_elec_{GWP}"],
        ),
        bscc=(
            par[f"ghgi_ng_base_scco2_{GWP}"],
            par_uu[f"ghgi_ng_base_scco2_{GWP}"],
            par_ul[f"ghgi_ng_base_scco2_{GWP}"],
        ),
        both=(
            par[f"ghgi_ng_base_other_{GWP}"] + par[f"ghgi_ng_base_cts_{GWP}"],
            par_uu[f"ghgi_ng_base_other_{GWP}"] + par_uu[f"ghgi_ng_base_cts_{GWP}"],
            par_ul[f"ghgi_ng_base_other_{GWP}"] + par_ul[f"ghgi_ng_base_cts_{GWP}"],
        ),
        mlr=(
            par['ghgi_ng_methaneleakage'],
            par_uu['ghgi_ng_methaneleakage'],
            par_ul['ghgi_ng_methaneleakage'],
        ),
        mghgi=par[f"ghgi_ng_methaneleakage_perrate_{GWP}"],
    )


def getGHGING(bdir, bele, bscc, both, mlr, mghgi):

    return {
        'direct': bdir,
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(e*mghgi for e in mlr),
        'other': both,
    }


def getGHGIParamsBlue(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception("Blue capture rate type unknown: {}".format(tech_type))

    return dict(
        bdir=(
            par[f"ghgi_blue_base_direct_{tech_type}_{GWP}"],
            par_uu[f"ghgi_blue_base_direct_{tech_type}_{GWP}"],
            par_ul[f"ghgi_blue_base_direct_{tech_type}_{GWP}"],
        ),
        bele=(
            par[f"ghgi_blue_base_elec_{tech_type}_{GWP}"],
            par_uu[f"ghgi_blue_base_elec_{tech_type}_{GWP}"],
            par_ul[f"ghgi_blue_base_elec_{tech_type}_{GWP}"],
        ),
        bscc=(
            par[f"ghgi_blue_base_scco2_{tech_type}_{GWP}"],
            par_uu[f"ghgi_blue_base_scco2_{tech_type}_{GWP}"],
            par_ul[f"ghgi_blue_base_scco2_{tech_type}_{GWP}"],
        ),
        both=(
            par[f"ghgi_blue_base_other_{tech_type}_{GWP}"] + par[f"ghgi_blue_base_cts_{tech_type}_{GWP}"],
            par_uu[f"ghgi_blue_base_other_{tech_type}_{GWP}"] + par_uu[f"ghgi_blue_base_cts_{tech_type}_{GWP}"],
            par_ul[f"ghgi_blue_base_other_{tech_type}_{GWP}"] + par_ul[f"ghgi_blue_base_cts_{tech_type}_{GWP}"],
        ),
        mlr=(
            par['ghgi_ng_methaneleakage'],
            par_uu['ghgi_ng_methaneleakage'],
            par_ul['ghgi_ng_methaneleakage'],
        ),
        mghgi=par[f"ghgi_blue_methaneleakage_perrate_{tech_type}_{GWP}"],
    )


def getGHGIBlue(bdir, bele, bscc, both, mlr, mghgi):

    return {
        'direct': bdir,
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(e*mghgi for e in mlr),
        'other': both,
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
        'elec': tuple(e/eff for e in eghgi),
        'other': b,
    }
