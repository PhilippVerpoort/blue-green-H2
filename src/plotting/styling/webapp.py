from src.plotting.styling.styling import adjustFontSizes


def addWebappSpecificStyling(figs: dict):
    for subfigName, plotlyFigure in figs.items():
        if plotlyFigure is None: continue

        fs_sm = 10
        fs_md = 12
        fs_lg = 14

        adjustFontSizes(subfigName, plotlyFigure, fs_sm, fs_md, fs_lg)
