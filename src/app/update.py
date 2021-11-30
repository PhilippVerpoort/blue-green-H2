from dash.exceptions import PreventUpdate

def updateScenarioInputSimple(scenarioInput: dict,
                              simple_gwp: str, simple_leakage: float, simple_ng_price: float, simple_lifetime: int, simple_irate: float,
                              simple_cost_green_capex_2020: float, simple_cost_green_capex_2050: float,
                              simple_cost_green_elec_2020: float,  simple_cost_green_elec_2050: float,
                              simple_green_ocf: int, simple_elecsrc: str, simple_elecsrc_custom: float,
                              simple_cost_blue_capex_heb: float, simple_cost_blue_capex_leb: float,
                              simple_cost_blue_cts_2020: float, simple_cost_blue_cts_2050: float,
                              simple_cost_blue_eff_heb: float, simple_cost_blue_eff_leb: float,
                              advanced_gwp: str, advanced_times: list, advanced_fuels):

    # update options
    scenarioInput['options']['gwp'] = simple_gwp
    scenarioInput['params']['cost_ng_price']['value'] = simple_ng_price
    scenarioInput['params']['lifetime']['value'] = simple_lifetime
    scenarioInput['params']['irate']['value'] = simple_irate/100

    for fuel in scenarioInput['fuels']:
        if scenarioInput['fuels'][fuel]['type'] not in ['ng', 'blue']: continue
        scenarioInput['fuels'][fuel]['methane_leakage'] = simple_leakage / 100

    # update green data
    scenarioInput['params']['cost_green_capex']['value'][2020] = simple_cost_green_capex_2020
    scenarioInput['params']['cost_green_capex']['value'][2050] = simple_cost_green_capex_2050
    scenarioInput['params']['green_ocf']['value'] = simple_green_ocf/100

    for fuel in scenarioInput['fuels']:
        if scenarioInput['fuels'][fuel]['type'] == 'green' and scenarioInput['fuels'][fuel]['elecsrc'] != 'mix':
            scenarioInput['fuels'][fuel]['elecsrc'] = simple_elecsrc
    if simple_elecsrc == 'custom':
        scenarioInput['params']['ci_green_elec']['value']['custom'][simple_gwp] = simple_elecsrc_custom
    else:
        scenarioInput['params']['ci_green_elec']['value']['custom'][simple_gwp] = \
            scenarioInput['params']['ci_green_elec']['value'][simple_elecsrc][simple_gwp]
    scenarioInput['params']['cost_green_elec']['value']['custom'][2020] = simple_cost_green_elec_2020
    scenarioInput['params']['cost_green_elec']['value']['custom'][2050] = simple_cost_green_elec_2050

    # update blue data
    scenarioInput['params']['cost_blue_capex']['value']['atr+hcrccs'][2020] = simple_cost_blue_capex_heb
    scenarioInput['params']['cost_blue_capex']['value']['smr+lcrccs'][2030] = simple_cost_blue_capex_heb
    scenarioInput['params']['cost_blue_capex']['value']['smr+lcrccs'][2050] = simple_cost_blue_capex_heb
    scenarioInput['params']['cost_blue_capex']['value']['atr+hcrccs'][2020] = simple_cost_blue_capex_leb
    scenarioInput['params']['cost_blue_capex']['value']['atr+hcrccs'][2030] = simple_cost_blue_capex_leb
    scenarioInput['params']['cost_blue_capex']['value']['atr+hcrccs'][2050] = simple_cost_blue_capex_leb
    scenarioInput['params']['cost_blue_cts']['value'][2020] = simple_cost_blue_cts_2020
    scenarioInput['params']['cost_blue_cts']['value'][2050] = simple_cost_blue_cts_2050
    scenarioInput['params']['cost_blue_eff']['value']['smr+lcrccs'] = simple_cost_blue_eff_heb
    scenarioInput['params']['cost_blue_eff']['value']['atr+hcrccs'] = simple_cost_blue_eff_leb

    return scenarioInput


def updateScenarioInputAdvanced(scenarioInput: dict,
                                simple_gwp: str, simple_leakage: float, simple_ng_price: float, simple_lifetime: int, simple_irate: float,
                                simple_cost_green_capex_2020: float, simple_cost_green_capex_2050: float,
                                simple_cost_green_elec_2020: float,  simple_cost_green_elec_2050: float,
                                simple_green_ocf: int, simple_elecsrc: str, simple_elecsrc_custom: float,
                                simple_cost_blue_capex_heb: float, simple_cost_blue_capex_leb: float,
                                simple_cost_blue_cts_2020: float, simple_cost_blue_cts_2050: float,
                                simple_cost_blue_eff_heb: float, simple_cost_blue_eff_leb: float,
                                advanced_gwp: str, advanced_times: list, advanced_fuels):
    # update GWP
    scenarioInput['options']['gwp'] = advanced_gwp

    # update times:
    scenarioInput['options']['times'] = []
    for item in advanced_times:
        t = item['i']
        if not isinstance(t, int): raise PreventUpdate()
        scenarioInput['options']['times'].append(t)

    scenarioInput['fuels'] = {}
    for row in advanced_fuels:
        newFuel = {
            'desc': row['desc'],
            'type': row['type'],
            'colour': row['colour'],
            'capture_rate': row['capture_rate'],
            'methane_leakage': row['methane_leakage'],
            'include_capex': row['include_capex'],
            'elecsrc': row['elecsrc']
        }

        scenarioInput['fuels'][row['fuel']] = newFuel

    return scenarioInput
