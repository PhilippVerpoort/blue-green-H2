import pandas as pd


known_tech_types = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']
known_elec_srcs = ['RE', 'fossil', 'share']


def calcCost(current_params: pd.DataFrame, fuel: dict):
    if fuel['type'] == 'fossil':
        return getCostNG(current_params, fuel)
    elif fuel['type'] == 'blue':
        p = getCostParamsBlue(current_params, fuel)
        return getCostBlue(**p)
    elif fuel['type'] == 'green':
        p = getCostParamsGreen(current_params, fuel)
        return getCostGreen(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel['type']}")


def getCostNG(pars: pd.DataFrame, fuel: dict):
    return {'fuel_cost': __getValAndUnc(pars, 'cost_ng_price')}


def getCostParamsBlue(pars: pd.DataFrame, fuel: dict):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception(f"Blue technology type unknown: {tech_type}")
    if tech_type == 'atr-ccs-93%-lowscco2':
        tech_type = 'atr-ccs-93%'

    i = __getVal(pars, 'irate')
    n = __getVal(pars, 'lifetime')

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, f"cost_blue_capex_{tech_type}") if fuel['include_capex'] else (0.0, 0.0, 0.0),
        c_fonm=__getValAndUnc(pars, f"cost_blue_fixedonm_{tech_type}"),
        c_vonm=__getValAndUnc(pars, f"cost_blue_varonm_{tech_type}"),
        flh=__getVal(pars, 'cost_blue_flh'),
        p_ng=__getValAndUnc(pars, 'cost_ng_price'),
        eff=__getVal(pars, f"blue_eff_{tech_type}"),
        p_el=__getValAndUnc(pars, 'cost_green_elec_fossil'),
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


def getCostParamsGreen(pars: pd.DataFrame, fuel: dict):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    i = __getVal(pars, 'irate')
    n = __getVal(pars, 'lifetime')

    if tech_type == 'fossil':
        share = 0.0
    elif tech_type == 'RE':
        share = 1.0
    else:
        share = pars.loc['green_share'].val

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=__getValAndUnc(pars, 'cost_green_capex'),
        c_fonm=__getVal(pars, 'cost_green_fixedonm'),
        c_vonm=__getValAndUnc(pars, 'cost_green_varonm'),
        ocf=__getVal(pars, 'green_ocf'),
        sh=share,
        pelre=__getValAndUnc(pars, 'cost_green_elec_RE'),
        pelfos=__getValAndUnc(pars, 'cost_green_elec_fossil'),
        eff=__getVal(pars, 'green_eff'),
        transp=__getVal(pars, 'cost_h2transp'),
    )


def getCostGreen(FCR, c_pl, c_fonm, c_vonm, ocf, sh, pelre, pelfos, eff, transp):
    ocf = sh*ocf + (1-sh)*1.0
    return {
        'cap_cost': tuple(FCR * c/(ocf*8760) for c in c_pl),
        'elec_cost': tuple((sh * pelre[i] + (1.0-sh) * pelfos[i]) / eff for i in range(3)),
        'fonm_cost': tuple(c_fonm * FCR * c/(ocf*8760) for c in c_pl),
        'vonm_cost': tuple(c for c in c_vonm),
        'tra_cost': (transp, 0.0, 0.0),
    }


def __getValAndUnc(pars: pd.DataFrame, pname: str):
    return tuple(val for idx, val in pars.loc[pname, ['val', 'uu', 'ul']].iteritems())


def __getVal(pars: pd.DataFrame, pname: str):
    return pars.loc[pname].val
