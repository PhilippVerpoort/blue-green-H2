known_tech_types = ['smr', 'smr+lcrccs', 'smr+hcrccs', 'atr+hcrccs']
known_elec_srcs = ['RE', 'mix', 'share']


def calcCost(params: tuple, fuel: dict):
    if fuel['type'] == 'ng':
        return getCostNG(*params, fuel)
    elif fuel['type'] == 'blue':
        p = getCostParamsBlue(*params, fuel)
        return getCostBlue(**p)
    elif fuel['type'] == 'green':
        p = getCostParamsGreen(*params, fuel)
        return getCostGreen(**p)
    else:
        raise Exception("Unknown fuel: {}".format(fuel['type']))


def getCostNG(par: dict, par_uu: dict, par_ul: dict, fuel: dict):
    r = par['cost_ng_price']
    r_uu = par_uu['cost_ng_price']
    r_ul = par_ul['cost_ng_price']

    return {'fuel_cost': (r, r_uu, r_ul)}


def getCostParamsBlue(par: dict, par_uu: dict, par_ul: dict, fuel: dict):
    tech_type = fuel['tech_type']
    if tech_type not in known_tech_types:
        raise Exception("Blue capture rate type unknown: {}".format(tech_type))

    i = par['irate']
    n = par['lifetime']

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=(
            par[f"cost_blue_capex_{tech_type}"] if fuel['include_capex'] else 0.0,
            par_uu[f"cost_blue_capex_{tech_type}"] if fuel['include_capex'] else 0.0,
            par_ul[f"cost_blue_capex_{tech_type}"] if fuel['include_capex'] else 0.0,
        ),
        flh=par['cost_blue_flh'],
        p_ng=(
            par['cost_ng_price'],
            par_uu['cost_ng_price'],
            par_ul['cost_ng_price'],
        ),
        eff=par[f"blue_eff_{tech_type}"],
        p_el = (
            par['cost_green_elec_mix'],
            par_uu['cost_green_elec_mix'],
            par_ul['cost_green_elec_mix'],
        ),
        eff_el=par[f"blue_eff_elec_{tech_type}"],
        c_CTS=(
            par['cost_blue_cts'],
            par_uu['cost_blue_cts'],
            par_ul['cost_blue_cts'],
        ),
        emi=par[f"cost_blue_emiForCTS_{tech_type}"],
        transp=par['cost_h2transp'],
    )


def getCostBlue(FCR, c_pl, flh, p_ng, eff, p_el, eff_el, c_CTS, emi, transp):
    return {
        'cap_cost': tuple(FCR * c/flh for c in c_pl),
        'fuel_cost': tuple(p/eff for p in p_ng),
        'elec_cost': tuple(p/eff_el for p in p_el),
        'cts_cost': tuple(c*emi for c in c_CTS),
        'tra_cost': (transp, 0.0, 0.0),
    }


def getCostParamsGreen(par: dict, par_uu: dict, par_ul: dict, fuel: dict):
    tech_type = fuel['tech_type']
    if tech_type not in known_elec_srcs:
        raise Exception(f"Green electricity source type unknown: {tech_type}")

    i = par['irate']
    n = par['lifetime']

    sharemix = par['green_share']
    if tech_type == 'mix':
        sharemix = 1.0
    elif tech_type == 'RE':
        sharemix = 0.0
    shareof = {
        'RE': (1-sharemix),
        'mix': sharemix,
    }

    ocf = shareof['RE'] * par['green_ocf'] + shareof['mix'] * 1.0

    if tech_type == 'share':
        p_el = (
           sum(shareof[tech_type]*par[f"cost_green_elec_{tech_type}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_uu[f"cost_green_elec_{tech_type}"] for tech_type in ['RE', 'mix']),
           sum(shareof[tech_type]*par_ul[f"cost_green_elec_{tech_type}"] for tech_type in ['RE', 'mix']),
        )
    else:
        p_el = (
            par[f"cost_green_elec_{tech_type}"],
            par_uu[f"cost_green_elec_{tech_type}"],
            par_ul[f"cost_green_elec_{tech_type}"],
        )

    return dict(
        FCR=i * (1 + i) ** n / ((1 + i) ** n - 1),
        c_pl=(
            par['cost_green_capex'] if fuel['include_capex'] else 0.0,
            par_uu['cost_green_capex'] if fuel['include_capex'] else 0.0,
            par_ul['cost_green_capex'] if fuel['include_capex'] else 0.0,
        ),
        ocf=ocf,
        p_el=p_el,
        eff=par['green_eff'],
        transp=par['cost_h2transp'],
    )


def getCostGreen(FCR, c_pl, ocf, p_el, eff, transp):
    return {
        'cap_cost': tuple(FCR * c/(ocf*8760) for c in c_pl),
        'elec_cost': tuple(p/eff for p in p_el),
        'tra_cost': (transp, 0.0, 0.0),
    }
