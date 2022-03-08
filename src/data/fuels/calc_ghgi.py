known_tech_types = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']
known_elec_srcs = ['RE', 'fossil', 'share']


def calcGHGI(params: dict, fuel: dict, gwp: str):
    if fuel['type'] == 'fossil':
        p = getGHGIParamsNG(*params, fuel, gwp)
        return getGHGING(**p)
    elif fuel['type'] == 'blue':
        p = getGHGIParamsBlue(*params, fuel, gwp)
        return getGHGIBlue(**p)
    elif fuel['type'] == 'green':
        p = getGHGIParamsGreen(*params, fuel, gwp)
        return getGHGIGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel['type']}")


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
        raise Exception(f"Blue technology type unknown: {tech_type}")
    if tech_type == 'atr-ccs-93%-lowscco2':
        tech_type = 'atr-ccs-93%'
        lowscco2 = '-lowscco2'
    else:
        lowscco2 = ''

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
            par[f"ghgi_blue_base_scco2_{tech_type}{lowscco2}_{GWP}"],
            par_uu[f"ghgi_blue_base_scco2_{tech_type}{lowscco2}_{GWP}"],
            par_ul[f"ghgi_blue_base_scco2_{tech_type}{lowscco2}_{GWP}"],
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
        transp=par['ghgi_h2transp'],
    )


def getGHGIBlue(bdir, bele, bscc, both, mlr, mghgi, transp):
    r = {
        'direct': bdir,
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(mlr[i]*mghgi for i in range(3)),
        'other': both,
    }

    r['transp'] = tuple(transp*sum(e[i] for e in r.values()) for i in range(3))

    return r


def getGHGIParamsGreen(par: dict, par_uu: dict, par_ul: dict, fuel: dict, GWP: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    share = par['green_share']
    if tech_type == 'fossil':
        share = 0.0
    elif tech_type == 'RE':
        share = 1.0

    return dict(
        b=(
            par[f"ghgi_green_base_{GWP}"],
            par_uu[f"ghgi_green_base_{GWP}"],
            par_ul[f"ghgi_green_base_{GWP}"],
        ),
        eff=par[f"green_eff"],
        sh=share,
        elre=(
            par[f"ghgi_green_elec_RE_{GWP}"],
            par_uu[f"ghgi_green_elec_RE_{GWP}"],
            par_ul[f"ghgi_green_elec_RE_{GWP}"],
        ),
        elfos=(
            par[f"ghgi_green_elec_fossil_{GWP}"],
            par_uu[f"ghgi_green_elec_fossil_{GWP}"],
            par_ul[f"ghgi_green_elec_fossil_{GWP}"],
        ),
        transp=par['ghgi_h2transp'],
    )


def getGHGIGreen(b, eff, sh, elre, elfos, transp):
    r = {
        'elec': tuple((sh * elre[i] + (1.0-sh) * elfos[i]) / eff for i in range(3)),
        'other': b,
    }

    r['transp'] = tuple(transp*sum(e[i] for e in r.values()) for i in range(3))

    return r
