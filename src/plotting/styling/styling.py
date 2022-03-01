import plotly.graph_objects as go


def adjustFontSizes(subfigName: str, plotlyFigure: go.Figure, fs_sm: float, fs_md: float, fs_lg: float):
    plotlyFigure.update_layout(font_size=fs_sm)
    plotlyFigure.update_xaxes(title_font_size=fs_sm, tickfont_size=fs_sm)
    plotlyFigure.update_yaxes(title_font_size=fs_sm, tickfont_size=fs_sm)

    plotlyFigure.update_annotations(font_size=fs_sm)
    numSubPlots = __countNumbSubplots(plotlyFigure)
    for annotation in plotlyFigure['layout']['annotations'][:numSubPlots]:
        annotation['font']['size'] = fs_lg

    subLabels = {
        'fig2a': 1,
        'fig2b': 1,
        'fig3': 4,
        'fig4': 1,
    }
    if subfigName in subLabels:
        for annotation in plotlyFigure['layout']['annotations'][numSubPlots:numSubPlots + subLabels[subfigName]]:
            annotation['font']['size'] = fs_md


def __countNumbSubplots(figure: go.Figure):
    return sum(1 for row in range(len(figure._grid_ref))
                 for col in range(len(figure._grid_ref[row]))
                 if figure._grid_ref[row][col] is not None) \
                 if figure._grid_ref is not None else 1
