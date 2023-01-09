import pandas as pd

from src.data.fuels.helper_funcs import getValAndUnc, getVal, simpleRetValUnc

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
        bdir=getValAndUnc(pars, 'ghgi_ng_base', {'component': 'direct', **options}),
        bele=getValAndUnc(pars, 'ghgi_ng_base', {'component': 'elec', **options}),
        bscc=getValAndUnc(pars, 'ghgi_ng_base', {'component': 'scco2', **options}),
        both=getValAndUnc(pars, 'ghgi_ng_base', {'component': 'other', **options}),
        mlr=getValAndUnc(pars, 'ghgi_ng_methaneleakage', options),
        mghgi=getVal(pars, 'ghgi_ng_methaneleakage_perrate', options),
    )


def getGHGING(bdir, bele, bscc, both, mlr, mghgi, calc_unc: bool = True):
    return {
        # direct emissions
        'direct': simpleRetValUnc(*bdir, 'ghgi_ng_base__direct', calc_unc),

        # elec emissions
        'elec': simpleRetValUnc(*bele, 'ghgi_ng_base__elec', calc_unc),

        # supply-chain CO2 emissions
        'scco2': simpleRetValUnc(*bscc, 'ghgi_ng_base__scco2', calc_unc),

        # supply-chain CH4 emissions
        'scch4': simpleRetValUnc(*(rate*mghgi for rate in mlr), 'ghgi_ng_methaneleakage', calc_unc),

        # other emissions
        'other': simpleRetValUnc(*both, 'ghgi_ng_base__other', calc_unc),
    }


def getGHGIParamsBlue(pars: pd.DataFrame, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    # special treatment for the assumption of low supply-chain CO2
    options_scco2 = options.copy()
    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    return dict(
        bdir=getValAndUnc(pars, 'ghgi_blue_base', {'component': 'direct', **options}),
        bele=getValAndUnc(pars, 'ghgi_blue_base', {'component': 'elec', **options}),
        bscc=getValAndUnc(pars, 'ghgi_blue_base', {'component': 'scco2', **options_scco2}),
        bcts=getValAndUnc(pars, 'ghgi_blue_base', {'component': 'cts', **options}),
        both=getValAndUnc(pars, 'ghgi_blue_base', {'component': 'other', **options}),
        cr=getValAndUnc(pars, 'ghgi_blue_capture_rate', options),
        crd=getVal(pars, 'ghgi_blue_capture_rate_default', options),
        mlr=getValAndUnc(pars, 'ghgi_ng_methaneleakage', options),
        mghgi=getVal(pars, 'ghgi_blue_methaneleakage_perrate', options),
        transp=getVal(pars, 'ghgi_h2transp', options),
    )


def getGHGIBlue(bdir, bele, bscc, bcts, both, cr, crd, mlr, mghgi, transp, calc_unc: bool = True):
    r = {
        # direct emissions
        'direct': {
            'val': (1 - cr[0]) / (1 - crd) * bdir[0],
        } | ({
            'uu': {
                'blue_capture_rate': - cr[1] / (1 - crd) * bdir[0],
                'ghgi_blue_base__direct': (1 - cr[0]) / (1 - crd) * bdir[1],
            },
            'ul': {
                'blue_capture_rate': - cr[2] / (1 - crd) * bdir[0],
                'ghgi_blue_base__direct': (1 - cr[0]) / (1 - crd) * bdir[2],
            },
        } if calc_unc else {}),

        # elec emissions
        'elec': simpleRetValUnc(*bele, 'ghgi_blue_base__elec', calc_unc),

        # supply-chain CO2 emissions
        'scco2': simpleRetValUnc(*bscc, 'ghgi_blue_base__scco2', calc_unc),

        # supply-chain CH4 emissions
        'scch4': simpleRetValUnc(*(rate*mghgi for rate in mlr), 'ghgi_ng_methaneleakage', calc_unc),

        # cts emissions
        'cts': simpleRetValUnc(*bcts, 'ghgi_blue_base__cts', calc_unc),

        # other emissions
        'other': simpleRetValUnc(*both, 'ghgi_blue_base__other', calc_unc),
    }

    # transport emissions relative to all other emissions
    r['transp'] = {
            'val': transp * sum(r[component]['val'] for component in r),
        } | ({
            ut: {
                pname: transp * r[component][ut][pname] for component in r for pname in r[component][ut]
            } for ut in ['uu', 'ul']
        } if calc_unc else {})

    return r


def getGHGIParamsGreen(pars: pd.DataFrame, options: dict):
    return dict(
        base=getValAndUnc(pars, 'ghgi_green_base', options),
        eff=getVal(pars, 'green_eff', options),
        sh=getValAndUnc(pars, 'green_share', options),
        elre=getValAndUnc(pars, 'ghgi_green_elec', {'elec_src': 'RE', **options}),
        elfos=getValAndUnc(pars, 'ghgi_green_elec', {'elec_src': 'fossil', **options}),
        transp=getVal(pars, 'ghgi_h2transp', options),
    )


def getGHGIGreen(base, eff, sh, elre, elfos, transp, calc_unc: bool = True):
    r = {
        # elec emissions
        'elec': {
            'val': (sh[0] * elre[0] + (1.0-sh[0]) * elfos[0]) / eff,
        } | ({
            'uu': {
                'green_share': sh[2] * (elre[0] - elfos[0]) / eff,
                'ghgi_green_elec__RE': sh[0] * elre[1] / eff,
            },
            'ul': {
                'green_share': sh[1] * (elre[0] - elfos[0]) / eff,
                'ghgi_green_elec__RE': sh[0] * elre[2] / eff,
            },
        } if calc_unc else {}),

        # other emissions
        'other': simpleRetValUnc(*base, 'ghgi_green_base', calc_unc),
    }

    # transport emissions relative to all other emissions
    r['transp'] = {
            'val': transp * sum(r[component]['val'] for component in r),
        } | ({
            ut: {
                pname: transp * r[component][ut][pname] for component in r for pname in r[component][ut]
            } for ut in ['uu', 'ul']
        } if calc_unc else {})

    return r
