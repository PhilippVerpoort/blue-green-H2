known_ESs = ['hydro', 'wind', 'solar', 'custom', 'mix']


def calcCost(params: dict, fuel: dict):
    if fuel['type'] == 'ng':
        return getCostNG(params, fuel)
    elif fuel['type'] == 'blue':
        p = getCostParamsBlue(params, fuel)
        return getCostBlue(**p)
    elif fuel['type'] == 'green':
        p = getCostParamsGreen(params, fuel)
        return getCostGreen(**p)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getCostNG(par: dict, fuel: dict):
    r = par['cost_ng_price']

    return {'fuel_cost': (r, 0.05*r)}


def getCostParamsBlue(par: dict, fuel: dict):
    CR = fuel['capture_rate']
    if fuel['capture_rate'] not in ['smr', 'heb', 'leb']: raise Exception("Blue capture rate type unknown: {}".format(CR))

    i = par['irate']
    n = par['lifetime']

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        C_pl=par[f"cost_blue_capex_{CR}"] if fuel['include_capex'] else 0.0,
        P_pl=par['cost_blue_plantsize'],
        flh=par['cost_blue_flh'],
        p_ng=par['cost_ng_price'],
        eff=par[f"cost_blue_eff_{CR}"],
        c_CTS=par['cost_blue_cts'],
        emi=par[f"cost_blue_emiForCTS_{CR}"],
    )


def getCostBlue(FCR, C_pl, P_pl, flh, p_ng, eff, c_CTS, emi):
    return {
        'cap_cost': (FCR * C_pl/(P_pl*flh),
                     FCR * C_pl/(P_pl*flh) * 0.05),
        'fuel_cost': (p_ng/eff,
                      p_ng/eff * 0.05),
        'cts_cost': (c_CTS*emi,
                     c_CTS*emi * 0.05),
    }


def getCostParamsGreen(par: dict, fuel: dict):
    ES = fuel['elecsrc']
    if ES not in known_ESs: raise Exception(f"Unknown elecsrc type: {ES}")

    i = par['irate']
    n = par['lifetime']

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=par['cost_green_capex'] if fuel['include_capex'] else 0.0,
        ocf=par['green_ocf'] if ES != 'mix' else 1.0,
        p_el=par[f"cost_green_elec_{ES}"],
        eff=par['ci_green_eff'],
    )


def getCostGreen(FCR, c_pl, ocf, p_el, eff):
    return {
        'cap_cost': (FCR * c_pl/(ocf*8760),
                     FCR * c_pl/(ocf*8760) * 0.05),
        'fuel_cost': (p_el*eff,
                      p_el*eff * 0.05),
    }
