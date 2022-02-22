import pandas as pd

from src.timeit import timeit


@timeit
def calcSteelData(fuelData: pd.DataFrame, steel_data: dict):
    fuelDataSteel = fuelData.copy()

    # Update cost and GHGI using H2 cost and GHGI data along with DRI-EAF data.
    fuelDataSteel['cost'] = fuelDataSteel['cost'] * steel_data['h2_demand'] + steel_data['other_cost']
    fuelDataSteel['cost_uu'] = fuelDataSteel['cost_uu'] * steel_data['h2_demand']
    fuelDataSteel['cost_ul'] = fuelDataSteel['cost_ul'] * steel_data['h2_demand']

    fuelDataSteel['ghgi'] = fuelDataSteel['ghgi'] * steel_data['h2_demand'] + steel_data['other_ghgi']
    fuelDataSteel['ghgi_uu'] = fuelDataSteel['ghgi_uu'] * steel_data['h2_demand']
    fuelDataSteel['ghgi_ul'] = fuelDataSteel['ghgi_ul'] * steel_data['h2_demand']

    # Create reference fuel for blast-furnace route.
    firstFuel = fuelDataSteel['fuel'].unique()[0]
    refFuel = fuelDataSteel.query(f"fuel=='{firstFuel}'").reset_index(drop=True)
    refFuel['fuel'] = 'blast furnace'
    refFuel['type'] = 'bf'
    refFuel['cost'] = steel_data['bf_cost']
    refFuel['cost_uu'] = 0.0
    refFuel['cost_ul'] = 0.0
    refFuel['ghgi'] = steel_data['bf_ghgi']
    refFuel['ghgi_uu'] = 0.0
    refFuel['ghgi_ul'] = 0.0

    return pd.concat([fuelDataSteel, refFuel], ignore_index=True)
