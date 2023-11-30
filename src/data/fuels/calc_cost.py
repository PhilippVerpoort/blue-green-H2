from src.data.fuels.helper_funcs import ParameterHandler, simpleRetValUnc


known_blue_techs = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']


def calcCost(param_handler: ParameterHandler, type: str, options: dict):
    p = paramsCost(param_handler, type, options)
    return evalCost(p, type)


def paramsCost(param_handler: ParameterHandler, type: str, options: dict):
    if type == 'NG':
        return getCostParamsNG(param_handler, options)
    elif type == 'BLUE':
        return getCostParamsBlue(param_handler, options)
    elif type == 'GREEN':
        return getCostParamsGreen(param_handler, options)
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


def getCostParamsNG(pm: ParameterHandler, options: dict):
    return dict(
        p_ng=pm.getValAndUnc('cost_ng_price', options),
        c_tnd=pm.getValAndUnc('cost_ng_grid', options),
    )


def getCostNG(p_ng, c_tnd, calc_unc: bool = True):
    return {
        # fuel cost = natural-gas price
        'fuel': simpleRetValUnc(*p_ng, 'cost_ng_price', calc_unc),

        # transport and distribution cost
        'tnd': simpleRetValUnc(*c_tnd, 'cost_ng_grid', calc_unc),
    }


def getCostParamsBlue(pm: ParameterHandler, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    # special treatment for the assumption of low supply-chain CO2
    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    i = pm.getVal('irate', options)
    n = pm.getVal('blue_lifetime', options)

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=pm.getValAndUnc('cost_blue_capex', options),
        c_fonm=pm.getValAndUnc('cost_blue_fixedonm', options),
        c_vonm=pm.getValAndUnc('cost_blue_varonm', options),
        flh=pm.getVal('cost_blue_flh', options),
        p_ng=pm.getValAndUnc('cost_ng_price', options),
        eff=pm.getValAndUnc('blue_eff', options),
        p_el=pm.getValAndUnc('cost_green_elec', options),
        eff_el=pm.getValAndUnc('blue_eff_elec', options),
        c_CTS=pm.getValAndUnc('cost_blue_cts', options),
        emi=pm.getVal('cost_blue_emiForCTS', options),
        transp=pm.getValAndUnc('cost_h2transp', options),
        cr=pm.getValAndUnc('ghgi_blue_capture_rate', options),
        crd=pm.getVal('ghgi_blue_capture_rate_default', options),
    )


def getCostBlue(FCR, c_pl, c_fonm, c_vonm, flh, p_ng, eff, p_el, eff_el, c_CTS, emi, transp, cr, crd, calc_unc: bool = True):
    return {
        # capital cost = fixed-charge rate * CAPEX / full-load hours
        'cap': simpleRetValUnc(*[FCR * c / flh for c in c_pl], 'blue_capex', calc_unc),

        # fuel cost = fuel price / efficiency
        'fuel': {
            'val': p_ng[0] / eff[0],
        } | ({
            'uu': {
                'cost_ng_price': p_ng[1] / eff[0],
                'blue_eff': - p_ng[0] * eff[2] / eff[0]**2,
            },
            'ul': {
                'cost_ng_price': p_ng[2] / eff[0],
                'blue_eff': - p_ng[0] * eff[1] / eff[0]**2,
            },
        } if calc_unc else {}),

        # elec cost = elec price / efficiency
        'elec': {
            'val': p_el[0] / eff_el[0],
        } | ({
            'uu': {
                'green_elec': p_el[1] / eff_el[0],
                'blue_eff_elec': - p_el[0] * eff_el[2] / eff_el[0]**2,
            },
            'ul': {
                'green_elec': p_el[2] / eff_el[0],
                'blue_eff_elec': - p_el[0] * eff_el[1] / eff_el[0]**2,
            },
        } if calc_unc else {}),

        # fixed operation and maintenance cost
        'fonm': simpleRetValUnc(*[c/flh for c in c_fonm], 'blue_fixedonm', calc_unc),

        # variable operation and maintenance cost
        'vonm': simpleRetValUnc(*c_vonm, 'blue_varonm', calc_unc),

        # carbon transport and storage cost = effective capture rate / default capture rate * default residual emissions * specific cost for transport and storage
        'cts': {
            'val': cr[0] / crd * emi * c_CTS[0],
        } | ({
            'uu': {
                'blue_capture_rate': cr[1] / crd * emi * c_CTS[0],
                'blue_cts': cr[0] / crd * emi * c_CTS[1],
            },
            'ul': {
                'blue_capture_rate': cr[2] / crd * emi * c_CTS[0],
                'blue_cts': cr[0] / crd * emi * c_CTS[2],
            },
        } if calc_unc else {}),

        # transport cost
        'tnd': simpleRetValUnc(*transp, 'cost_h2transp', calc_unc),
    }


def getCostParamsGreen(pm: ParameterHandler, options: dict):
    i = pm.getVal('irate', options)
    n = pm.getVal('green_lifetime', options)

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=pm.getValAndUnc('cost_green_capex', options),
        c_fonm=pm.getVal('cost_green_fixedonm', options),
        c_vonm=pm.getValAndUnc('cost_green_varonm', options),
        ocf=pm.getVal('green_ocf', options),
        p_el=pm.getValAndUnc('cost_green_elec', options),
        eff=pm.getVal('green_eff', options),
        transp=pm.getValAndUnc('cost_h2transp', options),
    )


def getCostGreen(FCR, c_pl, c_fonm, c_vonm, ocf, p_el, eff, transp, calc_unc: bool = True):
    return {
        # capital cost = fixed-charge rate * CAPEX / (operational-capacity factor * 8760 h/a)
        'cap': simpleRetValUnc(*[FCR * c / (ocf*8760) for c in c_pl], 'green_capex', calc_unc),

        # elec cost = elec price / efficiency
        'elec': simpleRetValUnc(*[p / eff for p in p_el], 'green_capex', calc_unc),

        # fixed operation and maintenance cost
        'fonm': simpleRetValUnc(*[c_fonm * FCR * c/(ocf*8760) for c in c_pl], 'blue_fixedonm', calc_unc),

        # variable operation and maintenance cost
        'vonm': simpleRetValUnc(*c_vonm, 'blue_varonm', calc_unc),

        # transport cost
        'tnd': simpleRetValUnc(*transp, 'cost_h2transp', calc_unc),
    }
