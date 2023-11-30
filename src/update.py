import yaml

from src.ctrls import cons_vs_prog_params, gas_prices_params, editTablesModal


# update callback function
def update_inputs(inputs_updated: dict, btn_pressed: str, args: list):
    simple_important_params = args[1]
    simple_gas_prices = args[2]
    simple_gwp = args[3]

    # update gwp option
    inputs_updated['options']['gwp'] = simple_gwp

    for casesType, paramList, tableName, data in [
        ('cons_vs_prog', cons_vs_prog_params, 'simple-important-params', simple_important_params),
        ('gas_prices', gas_prices_params, 'simple-gas-prices', simple_gas_prices)
    ]:
        for param, fuels in paramList.items():
            for fuel in fuels:
                for caseName in editTablesModal[tableName]:
                    row = next(i for i in range(len(data)) if data[i]['name'] == param)
                    inputs_updated['fuels'][fuel]['cases'][casesType][caseName][param] = yaml.load(
                        data[row][caseName], Loader=yaml.FullLoader
                    )
