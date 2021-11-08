from dash.exceptions import PreventUpdate

def updateScenarioInputSimple(scenarioInput: dict,
                              simple_gwp: str, simple_leakage: float,
                              advanced_gwp: str, advanced_times: list, advanced_fuels):
    # update GWP
    scenarioInput['options']['gwp'] = simple_gwp

    # update methane leakage
    for fuel in scenarioInput['fuels']:
        if scenarioInput['fuels'][fuel]['type'] not in ['ng', 'blue']: continue
        scenarioInput['fuels'][fuel]['methane_leakage'] = simple_leakage / 100

    return scenarioInput


def updateScenarioInputAdvanced(scenarioInput: dict,
                                simple_gwp: str, simple_leakage: float,
                                advanced_gwp: str, advanced_times: list, advanced_fuels):
    # update GWP
    scenarioInput['options']['gwp'] = advanced_gwp

    # update times:
    scenarioInput['options']['times'] = []
    for item in advanced_times:
        t = item['i']
        if not isinstance(t, int): raise PreventUpdate()
        scenarioInput['options']['times'].append(t)

    return scenarioInput
