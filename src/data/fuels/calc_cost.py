import pandas as pd

from src.config_load import params_options


known_blue_techs = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']


def calcCost(current_params: pd.DataFrame, type: str, options: dict):
    p = paramsCost(current_params, type, options)
    return evalCost(p, type)


def paramsCost(current_params: pd.DataFrame, type: str, options: dict):
    if type == 'NG':
        return getCostParamsNG(current_params, options)
    elif type == 'BLUE':
        return getCostParamsBlue(current_params, options)
    elif type == 'GREEN':
        return getCostParamsGreen(current_params, options)
    else:
        raise Exception(f"Unknown fuel: {type}")


def evalCost(p, type: str):
    if type == 'NG':
        return getCostNG(**p)
    elif type == 'BLUE':
        return getCostBlue(**p)
    elif type == 'GREEN':
        return getCostGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {type}")


def getCostParamsNG(pars: pd.DataFrame, options: dict):
    return dict(
        p_ng=__getValAndUnc(pars, 'cost_ng_price', options),
        c_tr=__getVal(pars, 'cost_ng_grid', options),
    )


def getCostNG(p_ng, c_tr):
    return {
        'fuel_cost': tuple(p for p in p_ng),
        'tra_cost': (c_tr, 0.0, 0.0),
    }


def getCostParamsBlue(pars: pd.DataFrame, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    i = __getVal(pars, 'irate', options)
    n = __getVal(pars, 'blue_lifetime', options)

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, 'cost_blue_capex', options),
        c_fonm=__getValAndUnc(pars, 'cost_blue_fixedonm', options),
        c_vonm=__getValAndUnc(pars, 'cost_blue_varonm', options),
        flh=__getVal(pars, 'cost_blue_flh', options),
        p_ng=__getValAndUnc(pars, 'cost_ng_price', options),
        eff=__getVal(pars, 'blue_eff', options),
        p_el=__getValAndUnc(pars, 'cost_green_elec', options),
        eff_el=__getVal(pars, 'blue_eff_elec', options),
        c_CTS=__getValAndUnc(pars, 'cost_blue_cts', options),
        emi=__getVal(pars, 'cost_blue_emiForCTS', options),
        transp=__getVal(pars, 'cost_h2transp', options),
        cr=__getVal(pars, 'ghgi_blue_capture_rate', options),
        crd=__getVal(pars, 'ghgi_blue_capture_rate_default', options),
    )


def getCostBlue(FCR, c_pl, c_fonm, c_vonm, flh, p_ng, eff, p_el, eff_el, c_CTS, emi, transp, cr, crd):
    return {
        'cap_cost': tuple(FCR * c/flh for c in c_pl),
        'fuel_cost': tuple(p/eff for p in p_ng),
        'elec_cost': tuple(p/eff_el for p in p_el),
        'fonm_cost': tuple(c/flh for c in c_fonm),
        'vonm_cost': tuple(c for c in c_vonm),
        'cts_cost': tuple(cr/crd*emi*c for c in c_CTS),
        'tra_cost': (transp, 0.0, 0.0),
    }


def getCostParamsGreen(pars: pd.DataFrame, options: dict):
    i = __getVal(pars, 'irate', options)
    n = __getVal(pars, 'green_lifetime', options)

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, 'cost_green_capex', options),
        c_fonm=__getVal(pars, 'cost_green_fixedonm', options),
        c_vonm=__getValAndUnc(pars, 'cost_green_varonm', options),
        ocf=__getVal(pars, 'green_ocf', options),
        p_el=__getValAndUnc(pars, 'cost_green_elec', options),
        eff=__getVal(pars, 'green_eff', options),
        transp=__getVal(pars, 'cost_h2transp', options),
    )


def getCostGreen(FCR, c_pl, c_fonm, c_vonm, ocf, p_el, eff, transp):
    return {
        'cap_cost': tuple(FCR * c/(ocf*8760) for c in c_pl),
        'elec_cost': tuple(p_el[i] / eff for i in range(3)),
        'fonm_cost': tuple(c_fonm * FCR * c/(ocf*8760) for c in c_pl),
        'vonm_cost': tuple(c for c in c_vonm),
        'tra_cost': (transp, 0.0, 0.0),
    }


def __getValAndUnc(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = __getFullPname(pname, options)
    return tuple(val for idx, val in pars.loc[pname_full, ['val', 'uu', 'ul']].iteritems())


def __getVal(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = __getFullPname(pname, options)
    return pars.loc[pname_full].val


def __getFullPname(pname: str, options: dict):
    return '_'.join([pname] + [options[t] for t in params_options[pname]])
