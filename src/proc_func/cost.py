from src.proc_func.helper import ParameterHandler, simple_ret_val_unc


known_blue_techs = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']


def calc_cost(param_handler: ParameterHandler, fuel_type: str, options: dict):
    p = params_cost(param_handler, fuel_type, options)
    return eval_cost(p, fuel_type)


def params_cost(param_handler: ParameterHandler, fuel_type: str, options: dict):
    if fuel_type == 'NG':
        return get_cost_params_ng(param_handler, options)
    elif fuel_type == 'BLUE':
        return get_cost_params_blue(param_handler, options)
    elif fuel_type == 'GREEN':
        return get_cost_params_green(param_handler, options)
    else:
        raise Exception(f"Unknown fuel: {fuel_type}")


def eval_cost(p, fuel_type: str):
    if fuel_type == 'NG':
        return get_cost_ng(**p)
    elif fuel_type == 'BLUE':
        return get_cost_blue(**p)
    elif fuel_type == 'GREEN':
        return get_cost_green(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel_type}")


def get_cost_params_ng(pm: ParameterHandler, options: dict):
    return dict(
        p_ng=pm.get_val_and_unc('cost_ng_price', options),
        c_tnd=pm.get_val_and_unc('cost_ng_grid', options),
    )


def get_cost_ng(p_ng, c_tnd, calc_unc: bool = True):
    return {
        # fuel cost = natural-gas price
        'fuel': simple_ret_val_unc(*p_ng, 'cost_ng_price', calc_unc),

        # transport and distribution cost
        'tnd': simple_ret_val_unc(*c_tnd, 'cost_ng_grid', calc_unc),
    }


def get_cost_params_blue(pm: ParameterHandler, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    # special treatment for the assumption of low supply-chain CO2
    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    i = pm.get_val('irate', options)
    n = pm.get_val('blue_lifetime', options)

    return dict(
        anf=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=pm.get_val_and_unc('cost_blue_capex', options),
        c_fonm=pm.get_val_and_unc('cost_blue_fixedonm', options),
        c_vonm=pm.get_val_and_unc('cost_blue_varonm', options),
        flh=pm.get_val('cost_blue_flh', options),
        p_ng=pm.get_val_and_unc('cost_ng_price', options),
        eff=pm.get_val_and_unc('blue_eff', options),
        p_el=pm.get_val_and_unc('cost_green_elec', options),
        eff_el=pm.get_val_and_unc('blue_eff_elec', options),
        c_cts=pm.get_val_and_unc('cost_blue_cts', options),
        emi=pm.get_val('cost_blue_emiForCTS', options),
        transp=pm.get_val_and_unc('cost_h2transp', options),
        cr=pm.get_val_and_unc('ghgi_blue_capture_rate', options),
        crd=pm.get_val('ghgi_blue_capture_rate_default', options),
    )


def get_cost_blue(anf, c_pl, c_fonm, c_vonm, flh, p_ng, eff, p_el, eff_el, c_cts, emi, transp, cr, crd,
                  calc_unc: bool = True):
    return {
        # capital cost = fixed-charge rate * CAPEX / full-load hours
        'cap': simple_ret_val_unc(*[anf * c / flh for c in c_pl], 'blue_capex', calc_unc),

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
        'fonm': simple_ret_val_unc(*[c / flh for c in c_fonm], 'blue_fixedonm', calc_unc),

        # variable operation and maintenance cost
        'vonm': simple_ret_val_unc(*c_vonm, 'blue_varonm', calc_unc),

        # carbon transport and storage cost = effective capture rate / default capture rate *
        #                                     default residual emissions * specific cost for transport and storage
        'cts': {
            'val': cr[0] / crd * emi * c_cts[0],
        } | ({
            'uu': {
                'blue_capture_rate': cr[1] / crd * emi * c_cts[0],
                'blue_cts': cr[0] / crd * emi * c_cts[1],
            },
            'ul': {
                'blue_capture_rate': cr[2] / crd * emi * c_cts[0],
                'blue_cts': cr[0] / crd * emi * c_cts[2],
            },
        } if calc_unc else {}),

        # transport cost
        'tnd': simple_ret_val_unc(*transp, 'cost_h2transp', calc_unc),
    }


def get_cost_params_green(pm: ParameterHandler, options: dict):
    i = pm.get_val('irate', options)
    n = pm.get_val('green_lifetime', options)

    return dict(
        anf=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=pm.get_val_and_unc('cost_green_capex', options),
        c_fonm=pm.get_val('cost_green_fixedonm', options),
        c_vonm=pm.get_val_and_unc('cost_green_varonm', options),
        ocf=pm.get_val('green_ocf', options),
        p_el=pm.get_val_and_unc('cost_green_elec', options),
        eff=pm.get_val('green_eff', options),
        transp=pm.get_val_and_unc('cost_h2transp', options),
    )


def get_cost_green(anf, c_pl, c_fonm, c_vonm, ocf, p_el, eff, transp, calc_unc: bool = True):
    return {
        # capital cost = fixed-charge rate * CAPEX / (operational-capacity factor * 8760 h/a)
        'cap': simple_ret_val_unc(*[anf * c / eff / (ocf * 8760) for c in c_pl], 'green_capex', calc_unc),

        # elec cost = elec price / efficiency
        'elec': simple_ret_val_unc(*[p / eff for p in p_el], 'green_capex', calc_unc),

        # fixed operation and maintenance cost
        'fonm': simple_ret_val_unc(*[c_fonm * anf * c / (ocf * 8760) for c in c_pl], 'blue_fixedonm', calc_unc),

        # variable operation and maintenance cost
        'vonm': simple_ret_val_unc(*c_vonm, 'blue_varonm', calc_unc),

        # transport cost
        'tnd': simple_ret_val_unc(*transp, 'cost_h2transp', calc_unc),
    }
