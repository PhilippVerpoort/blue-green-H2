from src.proc_func.helper import simple_ret_val_unc, ParameterHandler


known_blue_techs = ['smr-ccs-56%', 'atr-ccs-93%', 'atr-ccs-93%-lowscco2']


def calc_ghgi(param_handler: ParameterHandler, fuel_type: str, options: dict):
    p = params_ghgi(param_handler, fuel_type, options)
    return eval_ghgi(p, fuel_type)


def params_ghgi(param_handler: ParameterHandler, fuel_type: str, options: dict):
    if fuel_type == 'NG':
        return get_ghgi_params_ng(param_handler, options)
    elif fuel_type == 'BLUE':
        return get_ghgi_params_blue(param_handler, options)
    elif fuel_type == 'GREEN':
        return get_ghgi_params_green(param_handler, options)
    else:
        raise Exception(f"Unknown fuel type: {fuel_type}")


def eval_ghgi(p, fuel_type: str):
    if fuel_type == 'NG':
        return get_ghgi_ng(**p)
    elif fuel_type == 'BLUE':
        return get_ghgi_blue(**p)
    elif fuel_type == 'GREEN':
        return get_ghgi_green(**p)
    else:
        raise Exception(f"Unknown fuel: {fuel_type}")


def get_ghgi_params_ng(pm: ParameterHandler, options: dict):
    return dict(
        bdir=pm.get_val_and_unc('ghgi_ng_base', {'component': 'direct', **options}),
        bele=pm.get_val_and_unc('ghgi_ng_base', {'component': 'elec', **options}),
        bscc=pm.get_val_and_unc('ghgi_ng_base', {'component': 'scco2', **options}),
        both=pm.get_val_and_unc('ghgi_ng_base', {'component': 'other', **options}),
        mlr=pm.get_val_and_unc('ghgi_ng_methaneleakage', options),
        mghgi=pm.get_val('ghgi_ng_methaneleakage_perrate', options),
    )


def get_ghgi_ng(bdir, bele, bscc, both, mlr, mghgi, calc_unc: bool = True):
    return {
        # direct emissions
        'direct': simple_ret_val_unc(*bdir, 'ghgi_ng_base__direct', calc_unc),

        # elec emissions
        'elec': simple_ret_val_unc(*bele, 'ghgi_ng_base__elec', calc_unc),

        # supply-chain CO2 emissions
        'scco2': simple_ret_val_unc(*bscc, 'ghgi_ng_base__scco2', calc_unc),

        # supply-chain CH4 emissions
        'scch4': simple_ret_val_unc(*(rate * mghgi for rate in mlr), 'ghgi_ng_methaneleakage', calc_unc),

        # other emissions
        'other': simple_ret_val_unc(*both, 'ghgi_ng_base__other', calc_unc),
    }


def get_ghgi_params_blue(pm: ParameterHandler, options: dict):
    if options['blue_tech'] not in known_blue_techs:
        raise Exception(f"Unknown blue technology type: {options['blue_tech']}")

    # special treatment for the assumption of low supply-chain CO2
    options_scco2 = options.copy()
    if options['blue_tech'].endswith('-lowscco2'):
        options = options.copy()
        options['blue_tech'] = options['blue_tech'].rstrip('-lowscco2')

    return dict(
        bdir=pm.get_val_and_unc('ghgi_blue_base', {'component': 'direct', **options}),
        bele=pm.get_val_and_unc('ghgi_blue_base', {'component': 'elec', **options}),
        bscc=pm.get_val_and_unc('ghgi_blue_base', {'component': 'scco2', **options_scco2}),
        bcts=pm.get_val_and_unc('ghgi_blue_base', {'component': 'cts', **options}),
        both=pm.get_val_and_unc('ghgi_blue_base', {'component': 'other', **options}),
        cr=pm.get_val_and_unc('ghgi_blue_capture_rate', options),
        crd=pm.get_val('ghgi_blue_capture_rate_default', options),
        mlr=pm.get_val_and_unc('ghgi_ng_methaneleakage', options),
        mghgi=pm.get_val('ghgi_blue_methaneleakage_perrate', options),
        transp=pm.get_val('ghgi_h2transp', options),
    )


def get_ghgi_blue(bdir, bele, bscc, bcts, both, cr, crd, mlr, mghgi, transp, calc_unc: bool = True):
    r = {
        # direct emissions
        'direct': {
            'val': (1 - cr[0]) / (1 - crd) * bdir[0],
        } | ({
            'uu': {
                'blue_capture_rate': - cr[1] / (1 - crd) * bdir[0],
                'ghgi_blue_base__direct': (1 - cr[0]) / (1 - crd) * bdir[1],
            },
            'ul': {
                'blue_capture_rate': - cr[2] / (1 - crd) * bdir[0],
                'ghgi_blue_base__direct': (1 - cr[0]) / (1 - crd) * bdir[2],
            },
        } if calc_unc else {}),

        # elec emissions
        'elec': simple_ret_val_unc(*bele, 'ghgi_blue_base__elec', calc_unc),

        # supply-chain CO2 emissions
        'scco2': simple_ret_val_unc(*bscc, 'ghgi_blue_base__scco2', calc_unc),

        # supply-chain CH4 emissions
        'scch4': simple_ret_val_unc(*(rate * mghgi for rate in mlr), 'ghgi_ng_methaneleakage', calc_unc),

        # other emissions
        'other': simple_ret_val_unc(*[both[i] + bcts[i] for i in range(3)], 'ghgi_blue_base__other', calc_unc),
    }

    # transport emissions relative to all other emissions
    r['transp'] = {
            'val': transp * sum(r[component]['val'] for component in r),
        } | ({
            ut: {
                pname: transp * r[component][ut][pname] for component in r for pname in r[component][ut]
            } for ut in ['uu', 'ul']
        } if calc_unc else {})

    return r


def get_ghgi_params_green(pm: ParameterHandler, options: dict):
    return dict(
        base=pm.get_val_and_unc('ghgi_green_base', options),
        eff=pm.get_val('green_eff', options),
        sh=pm.get_val_and_unc('green_share', options),
        elre=pm.get_val_and_unc('ghgi_green_elec', {'elec_src': 'RE', **options}),
        elfos=pm.get_val_and_unc('ghgi_green_elec', {'elec_src': 'fossil', **options}),
        transp=pm.get_val('ghgi_h2transp', options),
    )


def get_ghgi_green(base, eff, sh, elre, elfos, transp, calc_unc: bool = True):
    r = {
        # elec emissions
        'elec': {
            'val': (sh[0] * elre[0] + (1.0-sh[0]) * elfos[0]) / eff,
        } | ({
            'uu': {
                'green_share': sh[2] * (elre[0] - elfos[0]) / eff,
                'ghgi_green_elec__RE': sh[0] * elre[1] / eff,
            },
            'ul': {
                'green_share': sh[1] * (elre[0] - elfos[0]) / eff,
                'ghgi_green_elec__RE': sh[0] * elre[2] / eff,
            },
        } if calc_unc else {}),

        # other emissions
        'other': simple_ret_val_unc(*base, 'ghgi_green_base', calc_unc),
    }

    # transport emissions relative to all other emissions
    r['transp'] = {
            'val': transp * sum(r[component]['val'] for component in r),
        } | ({
            ut: {
                pname: transp * r[component][ut][pname] for component in r for pname in r[component][ut]
            } for ut in ['uu', 'ul']
        } if calc_unc else {})

    return r
