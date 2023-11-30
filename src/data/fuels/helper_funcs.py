import pandas as pd


class ParameterHandler:
    def __init__(self, pars: pd.DataFrame, params_options: dict):
        self._pars: pd.DataFrame = pars
        self._params_options: dict = params_options

    def getValAndUnc(self, pname: str, options: dict):
        pname_full = self._getFullPname(pname, options)
        r = self._pars.loc[pname_full, ['val', 'uu', 'ul']]
        if pd.isna(r['uu']) or pd.isna(r['ul']):
            raise Exception(f"Trying to access the uncertainty of parameter {pname} with no uncertainty provided:\n{r}")
        return tuple(r)


    def getVal(self, pname: str, options: dict):
        pname_full = self._getFullPname(pname, options)
        r = self._pars.loc[pname_full, ['val', 'uu', 'ul']]
        if not pd.isna(r['uu']) or not pd.isna(r['ul']):
            raise Exception(f"Uncertainty of parameter '{pname}' provided but not used in calculation:\n{r}")
        return r.val


    def _getFullPname(self, pname: str, options: dict):
        return '_'.join([pname] + [options[t] for t in self._params_options[pname]])


def simpleRetValUnc(val, uu, ul, pname: str, calc_unc: bool):
    return {
        'val': val,
    } | ({
        'uu': {pname: uu},
        'ul': {pname: ul},
    } if calc_unc else {})
