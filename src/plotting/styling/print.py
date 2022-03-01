from src.plotting.styling.styling import adjustFontSizes


dpi = 300.0

inch_per_mm = 0.03937
inch_per_pt = 1 / 72


def addPrintSpecificStyling(figs: dict):
    for subfigName, plotlyFigure in figs.items():
        if plotlyFigure is None: continue

        fs_sm = __getFontSize(5.0)
        fs_md = __getFontSize(6.0)
        fs_lg = __getFontSize(7.0)

        adjustFontSizes(subfigName, plotlyFigure, fs_sm, fs_md, fs_lg)


def __getFontSize(size_pt: float):
    return dpi * inch_per_pt * size_pt


def getImageSize(width_mm: float, height_mm: float):
    width_px = int(dpi * inch_per_mm * width_mm)
    height_px = int(dpi * inch_per_mm * height_mm)

    return dict(
        width=width_px,
        height=height_px,
    )

