import pandas as pd


known_tech_types = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']
known_elec_srcs = ['RE', 'fossil', 'share']


def calcGHGI(current_params: pd.DataFrame, fuel: dict, gwp: str):
    if fuel['type'] == 'fossil':
        p = getGHGIParamsNG(current_params, fuel, gwp)
        return getGHGING(**p)
    elif fuel['type'] == 'blue':
        p = getGHGIParamsBlue(current_params, fuel, gwp)
        return getGHGIBlue(**p)
    elif fuel['type'] == 'green':
        p = getGHGIParamsGreen(current_params, fuel, gwp)
        return getGHGIGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel['type']}")


def getGHGIParamsNG(pars: pd.DataFrame, fuel: dict, gwp: str):
    return dict(
        bdir=__getValAndUnc(pars, f"ghgi_ng_base_direct_{gwp}"),
        bele=__getValAndUnc(pars, f"ghgi_ng_base_elec_{gwp}"),
        bscc=__getValAndUnc(pars, f"ghgi_ng_base_scco2_{gwp}"),
        both=__getValAndUnc(pars, f"ghgi_ng_base_other_{gwp}"),
        mlr=__getValAndUnc(pars, 'ghgi_ng_methaneleakage'),
        mghgi=__getVal(pars, f"ghgi_ng_methaneleakage_perrate_{gwp}"),
    )


def getGHGING(bdir, bele, bscc, both, mlr, mghgi):

    return {
        'direct': bdir,
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(e*mghgi for e in mlr),
        'other': both,
    }


def getGHGIParamsBlue(pars: pd.DataFrame, fuel: dict, gwp: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception(f"Blue technology type unknown: {tech_type}")
    if tech_type == 'atr-ccs-93%-lowscco2':
        tech_type = 'atr-ccs-93%'
        lowscco2 = '-lowscco2'
    else:
        lowscco2 = ''

    # add cts ghgi to other
    poth = pars.loc[f"ghgi_blue_base_other_{tech_type}_{gwp}", ['val', 'uu', 'ul']] \
         + pars.loc[f"ghgi_blue_base_cts_{tech_type}_{gwp}", ['val', 'uu', 'ul']]

    return dict(
        bdir=__getValAndUnc(pars, f"ghgi_blue_base_direct_{tech_type}_{gwp}"),
        bele=__getValAndUnc(pars, f"ghgi_blue_base_elec_{tech_type}_{gwp}"),
        bscc=__getValAndUnc(pars, f"ghgi_blue_base_scco2_{tech_type}{lowscco2}_{gwp}"),
        both=(poth.val, poth.uu, poth.ul),
        mlr=__getValAndUnc(pars, 'ghgi_ng_methaneleakage'),
        mghgi=__getVal(pars, f"ghgi_blue_methaneleakage_perrate_{tech_type}_{gwp}"),
        transp=__getVal(pars, 'ghgi_h2transp'),
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


def getGHGIParamsGreen(pars: pd.DataFrame, fuel: dict, gwp: str):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    if tech_type == 'fossil':
        share = 0.0
    elif tech_type == 'RE':
        share = 1.0
    else:
        share = pars.loc['green_share'].val

    return dict(
        b=__getValAndUnc(pars, f"ghgi_green_base_{gwp}"),
        eff=__getVal(pars, 'green_eff'),
        sh=share,
        elre=__getValAndUnc(pars, f"ghgi_green_elec_RE_{gwp}"),
        elfos=__getValAndUnc(pars, f"ghgi_green_elec_fossil_{gwp}"),
        transp=__getVal(pars, 'ghgi_h2transp'),
    )


def getGHGIGreen(b, eff, sh, elre, elfos, transp):
    r = {
        'elec': tuple((sh * elre[i] + (1.0-sh) * elfos[i]) / eff for i in range(3)),
        'other': b,
    }

    r['transp'] = tuple(transp*sum(e[i] for e in r.values()) for i in range(3))

    return r


def __getValAndUnc(pars: pd.DataFrame, pname: str):
    return tuple(val for idx, val in pars.loc[pname, ['val', 'uu', 'ul']].iteritems())


def __getVal(pars: pd.DataFrame, pname: str):
    return pars.loc[pname].val
