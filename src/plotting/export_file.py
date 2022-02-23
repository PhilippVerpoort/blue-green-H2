import plotly.graph_objects as go

from src.config_load import figure_print
from src.filepaths import getFilePathOutput


dpi = 300.0

inch_per_mm = 0.03937
inch_per_pt = 1 / 72


def exportFigsToFiles(figs: dict):
    for subfigName, plotlyFigure in figs.items():
        if plotlyFigure is None: continue

        w_mm, h_mm = figure_print[subfigName]['size']

        fs_sm = __getFontSize(5.0)
        fs_lg = __getFontSize(7.0)

        plotlyFigure.update_layout(font_size=fs_sm)
        plotlyFigure.update_xaxes(title_font_size=fs_sm, tickfont_size=fs_sm)
        plotlyFigure.update_yaxes(title_font_size=fs_sm, tickfont_size=fs_sm)

        plotlyFigure.update_annotations(font_size=fs_sm)
        numSubPlots=__countNumbSubplots(plotlyFigure)
        if numSubPlots > 1:
            for annotation in plotlyFigure['layout']['annotations'][:numSubPlots]:
                annotation['font']['size'] = fs_lg
        else:
            plotlyFigure.update_annotations(font_size=fs_lg)

        plotlyFigure.write_image(getFilePathOutput(f"{subfigName}.png"), **__getImageSize(w_mm, h_mm))


def updateFontSizeWebapp(figs: dict):
    for subfigName, plotlyFigure in figs.items():
        if plotlyFigure is None: continue

        fs_sm = 10
        fs_lg = 14

        plotlyFigure.update_layout(font_size=fs_sm)
        plotlyFigure.update_xaxes(title_font_size=fs_sm, tickfont_size=fs_sm)
        plotlyFigure.update_yaxes(title_font_size=fs_sm, tickfont_size=fs_sm)

        plotlyFigure.update_annotations(font_size=fs_sm)
        numSubPlots=__countNumbSubplots(plotlyFigure)
        if numSubPlots > 1:
            for annotation in plotlyFigure['layout']['annotations'][:numSubPlots]:
                annotation['font']['size'] = fs_lg
        else:
            plotlyFigure.update_annotations(font_size=fs_lg)


def __getFontSize(size_pt: float):
    return dpi * inch_per_pt * size_pt


def __getImageSize(width_mm: float, height_mm: float):
    width_px = int(dpi * inch_per_mm * width_mm)
    height_px = int(dpi * inch_per_mm * height_mm)

    return dict(
        width=width_px,
        height=height_px,
    )


def __countNumbSubplots(figure: go.Figure):
    return sum(1 for row in range(len(figure._grid_ref))
                 for col in range(len(figure._grid_ref[row]))
                 if figure._grid_ref[row][col] is not None) \
                 if figure._grid_ref is not None else 1
