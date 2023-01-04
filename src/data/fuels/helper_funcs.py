import pandas as pd

from src.config_load import params_options


def getValAndUnc(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = getFullPname(pname, options)
    r = pars.loc[pname_full, ['val', 'uu', 'ul']]
    if pd.isna(r['uu']) or pd.isna(r['ul']):
        raise Exception(f"Trying to access the uncertainty of parameter {pname} with no uncertainty provided:\n{r}")
    return tuple(r)


def getVal(pars: pd.DataFrame, pname: str, options: dict):
    pname_full = getFullPname(pname, options)
    r = pars.loc[pname_full, ['val', 'uu', 'ul']]
    if not pd.isna(r['uu']) or not pd.isna(r['ul']):
        raise Exception(f"Uncertainty of parameter '{pname}' provided but not used in calculation:\n{r}")
    return r.val


def simpleRetValUnc(val, uu, ul, pname: str, calc_unc: bool):
    return {
        'val': val,
    } | ({
        'uu': {pname: uu},
        'ul': {pname: ul},
    } if calc_unc else {})


def getFullPname(pname: str, options: dict):
    return '_'.join([pname] + [options[t] for t in params_options[pname]])
