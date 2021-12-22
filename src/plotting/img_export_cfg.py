dpi = 300.0

inch_per_mm = 0.03937
inch_per_pt = 1 / 72


def getImageSize(width_mm: float, height_mm: float):
    width_px = int(dpi * inch_per_mm * width_mm)
    height_px = int(dpi * inch_per_mm * height_mm)

    return dict(
        width=width_px,
        height=height_px,
    )


def getFontSize(size_pt: float):
    return dpi * inch_per_pt * size_pt
