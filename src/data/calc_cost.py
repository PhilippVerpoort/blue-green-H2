def calcCost(params: dict, coeffs: dict, fuel: dict, consts: dict):
    if fuel['type'] == 'ng':
        return __calcNG(params, consts, coeffs, fuel)
    elif fuel['type'] == 'blue':
        return __calcBlue(params, consts, coeffs, fuel)
    elif fuel['type'] == 'green':
        return __calcGreen(params, consts, coeffs, fuel)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def __calcNG(par: dict, const: dict, coef: dict, fuel: dict):
    r = par['cost_ng_price']

    return (r, 0.05*r)


def __calcBlue(par: dict, const: dict, coef: dict, fuel: dict):
    CR = fuel['capture_rate']
    if CR not in ['smr', 'heb', 'leb']: raise Exception("Blue capture rate type unknown: {}".format(CR))

    C_pl = par[f"cost_blue_capex_{CR}"] if fuel['include_capex'] else 0.0
    P_pl = par['cost_blue_plantsize']
    p_ng = par['cost_ng_price']
    eff = par[f"cost_blue_eff_{CR}"]
    c_CTS = par['cost_blue_cts']
    flh = par['cost_blue_flh']
    emi = par[f"cost_blue_emiForCTS_{CR}"]

    i = par['irate']
    n = par['lifetime']
    FCR = i*(1+i)**n/((1+i)**n-1)

    r = FCR * C_pl/(P_pl*flh) + p_ng/eff + c_CTS*emi

    return (r, 0.05*r)


def __calcGreen(par: dict, const: dict, coef: dict, fuel: dict):
    ES = fuel['elecsrc']
    if ES not in ['re', 'mix']: raise Exception(f"Unknown elecsrc type: {ES}")

    c_pl = par['cost_green_capex']
    p_el = par[f"cost_green_elec_{ES}"]
    eff = par['ci_green_eff']
    ocf = par['green_ocf'] if ES=='re' else 1.0

    i = par['irate']
    n = par['lifetime']
    FCR = i*(1+i)**n/((1+i)**n-1)

    r = FCR * c_pl/(ocf*8760) + p_el*eff

    return (r, 0.05*r)
