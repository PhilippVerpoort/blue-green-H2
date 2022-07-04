import pandas as pd


def calcCost(current_params: pd.DataFrame, fuel: dict):
    if fuel['type'] == 'fossil':
        return getCostNG(current_params)
    elif fuel['type'] == 'blue':
        tech_type = __getTechType(fuel)
        p = getCostParamsBlue(current_params, tech_type)
        return getCostBlue(**p)
    elif fuel['type'] == 'green':
        p = getCostParamsGreen(current_params)
        return getCostGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel['type']}")


def __getTechType(fuel: dict):
    known_tech_types = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']

    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception(f"Blue technology type unknown: {tech_type}")
    if tech_type == 'atr-ccs-93%-lowscco2':
        tech_type = 'atr-ccs-93%'

    return tech_type


def getCostNG(pars: pd.DataFrame):
    return {'fuel_cost': __getValAndUnc(pars, 'cost_ng_price')}


def getCostParamsBlue(pars: pd.DataFrame, tech_type: str):
    i = __getVal(pars, 'irate')
    n = __getVal(pars, 'lifetime')

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, f"cost_blue_capex_{tech_type}"),
        c_fonm=__getValAndUnc(pars, f"cost_blue_fixedonm_{tech_type}"),
        c_vonm=__getValAndUnc(pars, f"cost_blue_varonm_{tech_type}"),
        flh=__getVal(pars, 'cost_blue_flh'),
        p_ng=__getValAndUnc(pars, 'cost_ng_price'),
        eff=__getVal(pars, f"blue_eff_{tech_type}"),
        p_el=__getValAndUnc(pars, 'cost_green_elec'),
        eff_el=__getVal(pars, f"blue_eff_elec_{tech_type}"),
        c_CTS=__getValAndUnc(pars, 'cost_blue_cts'),
        emi=__getVal(pars, f"cost_blue_emiForCTS_{tech_type}"),
        transp=__getVal(pars, 'cost_h2transp'),
    )


def getCostBlue(FCR, c_pl, c_fonm, c_vonm, flh, p_ng, eff, p_el, eff_el, c_CTS, emi, transp):
    return {
        'cap_cost': tuple(FCR * c/flh for c in c_pl),
        'fuel_cost': tuple(p/eff for p in p_ng),
        'elec_cost': tuple(p/eff_el for p in p_el),
        'fonm_cost': tuple(c/flh for c in c_fonm),
        'vonm_cost': tuple(c for c in c_vonm),
        'cts_cost': tuple(c*emi for c in c_CTS),
        'tra_cost': (transp, 0.0, 0.0),
    }


def getCostParamsGreen(pars: pd.DataFrame):
    i = __getVal(pars, 'irate')
    n = __getVal(pars, 'lifetime')

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, 'cost_green_capex'),
        c_fonm=__getVal(pars, 'cost_green_fixedonm'),
        c_vonm=__getValAndUnc(pars, 'cost_green_varonm'),
        ocf=__getVal(pars, 'green_ocf'),
        p_el=__getValAndUnc(pars, 'cost_green_elec'),
        eff=__getVal(pars, 'green_eff'),
        transp=__getVal(pars, 'cost_h2transp'),
    )


def getCostGreen(FCR, c_pl, c_fonm, c_vonm, ocf, p_el, eff, transp):
    return {
        'cap_cost': tuple(FCR * c/(ocf*8760) for c in c_pl),
        'elec_cost': tuple(p_el[i] / eff for i in range(3)),
        'fonm_cost': tuple(c_fonm * FCR * c/(ocf*8760) for c in c_pl),
        'vonm_cost': tuple(c for c in c_vonm),
        'tra_cost': (transp, 0.0, 0.0),
    }


def __getValAndUnc(pars: pd.DataFrame, pname: str):
    return tuple(val for idx, val in pars.loc[pname, ['val', 'uu', 'ul']].iteritems())


def __getVal(pars: pd.DataFrame, pname: str):
    return pars.loc[pname].val
