import pandas as pd

from src.config_load import params_options


known_blue_techs = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']


def calcGHGI(current_params: pd.DataFrame, type: str, options: dict):
    p = paramsGHGI(current_params, type, options)
    return evalGHGI(p, type)


def paramsGHGI(current_params: pd.DataFrame, type: str, options: dict):
    if type == 'NG':
        return getGHGIParamsNG(current_params, options)
    elif type == 'BLUE':
        return getGHGIParamsBlue(current_params, options)
    elif type == 'GREEN':
        return getGHGIParamsGreen(current_params, options)
    else:
        raise Exception(f"Unknown fuel type: {type}")


def evalGHGI(p, type: str):
    if type == 'NG':
        return getGHGING(**p)
    elif type == 'BLUE':
        return getGHGIBlue(**p)
    elif type == 'GREEN':
        return getGHGIGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {type}")


def getGHGIParamsNG(pars: pd.DataFrame, options: dict):
    return dict(
        bdir=__getValAndUnc(pars, 'ghgi_ng_base', {'component': 'direct', **options}),
        bele=__getValAndUnc(pars, 'ghgi_ng_base', {'component': 'elec', **options}),
        bscc=__getValAndUnc(pars, 'ghgi_ng_base', {'component': 'scco2', **options}),
        both=__getValAndUnc(pars, 'ghgi_ng_base', {'component': 'other', **options}),
        mlr=__getValAndUnc(pars, 'ghgi_ng_methaneleakage', options),
        mghgi=__getVal(pars, 'ghgi_ng_methaneleakage_perrate', options),
    )


def getGHGING(bdir, bele, bscc, both, mlr, mghgi):
    return {
        'direct': bdir,
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(e*mghgi for e in mlr),
        'other': both,
    }


def getGHGIParamsBlue(pars: pd.DataFrame, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    options_scco2 = options.copy()
    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    return dict(
        bdir=__getValAndUnc(pars, 'ghgi_blue_base', {'component': 'direct', **options}),
        bele=__getValAndUnc(pars, 'ghgi_blue_base', {'component': 'elec', **options}),
        bscc=__getValAndUnc(pars, 'ghgi_blue_base', {'component': 'scco2', **options_scco2}),
        bcts=__getValAndUnc(pars, 'ghgi_blue_base', {'component': 'cts', **options}),
        both=__getValAndUnc(pars, 'ghgi_blue_base', {'component': 'other', **options}),
        cr=__getVal(pars, 'ghgi_blue_capture_rate', options),
        crd=__getVal(pars, 'ghgi_blue_capture_rate_default', options),
        mlr=__getValAndUnc(pars, 'ghgi_ng_methaneleakage', options),
        mghgi=__getVal(pars, 'ghgi_blue_methaneleakage_perrate', options),
        transp=__getVal(pars, 'ghgi_h2transp', options),
    )


def getGHGIBlue(bdir, bele, bscc, bcts, both, cr, crd, mlr, mghgi, transp):
    r = {
        'direct': tuple((1-cr)/(1-crd)*bdir[i] for i in range(3)),
        'elec': bele,
        'scco2': bscc,
        'scch4': tuple(mlr[i]*mghgi for i in range(3)),
        'other': tuple(bcts[i]+both[i] for i in range(3)),
    }

    r['transp'] = tuple(transp*sum(e[i] for e in r.values()) for i in range(3))

    return r


def getGHGIParamsGreen(pars: pd.DataFrame, options: dict):
    return dict(
        b=__getValAndUnc(pars, 'ghgi_green_base', options),
        eff=__getVal(pars, 'green_eff', options),
        sh=__getVal(pars, 'green_share', options),
        elre=__getValAndUnc(pars, 'ghgi_green_elec', {'elec_src': 'RE', **options}),
        elfos=__getValAndUnc(pars, 'ghgi_green_elec', {'elec_src': 'fossil', **options}),
        transp=__getVal(pars, 'ghgi_h2transp', options),
    )


def getGHGIGreen(b, eff, sh, elre, elfos, transp):
    r = {
        'elec': tuple((sh * elre[i] + (1.0-sh) * elfos[i]) / eff for i in range(3)),
        'other': b,
    }

    r['transp'] = tuple(transp*sum(e[i] for e in r.values()) for i in range(3))

    return r


def __getValAndUnc(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = __getFullPname(pname, options)
    return tuple(val for idx, val in pars.loc[pname_full, ['val', 'uu', 'ul']].iteritems())


def __getVal(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = __getFullPname(pname, options)
    return pars.loc[pname_full].val


def __getFullPname(pname: str, options: dict):
    return '_'.join([pname] + [options[t] for t in params_options[pname]])
