import pandas as pd


class ParameterHandler:
    def __init__(self, pars: pd.DataFrame, params_options: dict):
        self._pars: pd.DataFrame = pars
        self._params_options: dict = params_options

    def get_val_and_unc(self, pname: str, options: dict):
        pname_full = self._get_full_pname(pname, options)
        r = self._pars.loc[pname_full, ['val', 'uu', 'ul']]
        if pd.isna(r['uu']) or pd.isna(r['ul']):
            raise Exception(f"Trying to access the uncertainty of parameter {pname} with no uncertainty provided:\n{r}")
        return tuple(r)

    def get_val(self, pname: str, options: dict):
        pname_full = self._get_full_pname(pname, options)
        r = self._pars.loc[pname_full, ['val', 'uu', 'ul']]
        if not pd.isna(r['uu']) or not pd.isna(r['ul']):
            raise Exception(f"Uncertainty of parameter '{pname}' provided but not used in calculation:\n{r}")
        return r.val

    def _get_full_pname(self, pname: str, options: dict):
        return '_'.join([pname] + [options[t] for t in self._params_options[pname]])


def simple_ret_val_unc(val, uu, ul, pname: str, calc_unc: bool):
    return {
        'val': val,
    } | ({
        'uu': {pname: uu},
        'ul': {pname: ul},
    } if calc_unc else {})
