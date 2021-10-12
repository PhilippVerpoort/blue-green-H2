import math


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
    # convert €/GJ to €/MWh
    return par['ng_price'] / const['J_to_Wh'] / 1000


def __calcBlue(par: dict, const: dict, coef: dict, fuel: dict):
    CR = fuel['capture_rate']
    if CR not in ['smr', 'heb', 'leb']: raise Exception("Blue capture rate type unknown: {}".format(CR))

    FC = par['ng_price']
    CC = par['cost_blue_capital_'+CR] if fuel['include_capex'] else 0.0
    CTS = par['cost_blue_cts'] if CR!='smr' else 0.0

    gamma = coef['gamma_blue_'+CR]
    alpha = coef['alpha_blue']
    delta = coef['delta_blue']

    convFac1 = 1000.0  # from €/kWh to €/MWh
    convFac2 = const['NM3_to_kWh']  # from norm cubic meter to kWh_LHV

    # final output in €/MWh
    return convFac1/convFac2 * ( gamma*FC + alpha*CC + delta*CTS )


def __calcGreen(par: dict, const: dict, coef: dict, fuel: dict):
    CC = par['cost_green_electrolyser']

    if fuel['elecsrc'] == 'RE only':
        FC = par['cost_green_electricity_re']
        OCF = par['capacity_factor_re']
    elif fuel['elecsrc'] == 'grid mix':
        FC = par['cost_green_electricity_mix']
        OCF = 100.0
    else:
        raise Exception("Unknown elecsrc type: {}".format(fuel['elecsrc']))

    gamma = coef['gamma_green']
    alpha = coef['alpha_green']
    delta = coef['delta_green']
    tau   = coef['tau_green']
    theta = coef['theta_green']

    convFac1 = const['USD_to_EUR']
    convFac2 = const['kgH2_to_kWh_HHV'] / 1000

    # final output in €/MWh
    return convFac1/convFac2 * ( gamma*FC + (alpha*CC + delta)*(tau*math.pow(OCF, -theta)) )