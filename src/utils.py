import pathlib

import pandas as pd
import yaml


BASE_PATH = pathlib.Path(__file__).parent.parent.resolve()


def load_csv_data_file(base_name: str):
    path = BASE_PATH / 'data' / f"{base_name}.csv"
    return pd.read_csv(path)


def load_yaml_data_file(base_name: str):
    path = BASE_PATH / 'data' / f"{base_name}.yml"
    with open(path, 'r') as f:
        ret = yaml.load(f.read(), Loader=yaml.FullLoader)
    return ret


def load_yaml_config_file(base_name: str):
    path = BASE_PATH / 'config' / f"{base_name}.yml"
    with open(path, 'r') as f:
        ret = yaml.load(f.read(), Loader=yaml.FullLoader)
    return ret


def load_yaml_plot_config_file(base_name: str):
    path = BASE_PATH / 'config' / 'plots' / f"{base_name}.yml"
    with open(path, 'r') as f:
        ret = yaml.load(f.read(), Loader=yaml.FullLoader)
    return ret['figures'], ret['config']
