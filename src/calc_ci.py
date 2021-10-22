def calcCI(params: dict, coeffs: dict, fuel: dict, consts: dict):
    if fuel['type'] == 'ng':
        return __calcNG(params, consts, coeffs, fuel)
    elif fuel['type'] == 'blue':
        return __calcBlue(params, consts, coeffs, fuel)
    elif fuel['type'] == 'green':
        return __calcGreen(params, consts, coeffs, fuel)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def __calcNG(par: dict, const: dict, coef: dict, fuel: dict):
    # convert gCO2eq/MJ to tCO2eq/MWh
    r = par['ng_ci'] / const['J_to_Wh'] / 1000 / 1000

    return (r, 0.05*r)


def __calcBlue(par: dict, const: dict, coef: dict, fuel: dict):
    CR = fuel['capture_rate']

    r, _ = __calcNG(par, const, coef, fuel)

    if CR == 'smr':
        r *= 1.5
    elif CR == 'heb':
        r *= 1.5 * 1.6 * (1-0.6)
    elif CR == 'leb':
        r *= 1.5 * 1.7 * (1-0.9)

    return (r, 0.05*r)


def __calcGreen(par: dict, const: dict, coef: dict, fuel: dict):
    # convert gCO2eq/MWh to tCO2eq/kWh
    if fuel['elecsrc'] == 'RE only':
        r = par['ci_green_electricity_re'] / 1000
    elif fuel['elecsrc'] == 'grid mix':
        r = par['ci_green_electricity_mix'] / 1000
    else:
        raise Exception("Unknown elecsrc type!")

    return (r, 0.05*r)