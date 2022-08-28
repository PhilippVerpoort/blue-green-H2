from string import ascii_lowercase

import plotly.graph_objects as go


def adjustFontSizes(subfigName: str, plotlyFigure: go.Figure, fs_sm: float, fs_md: float, fs_lg: float):
    plotlyFigure.update_layout(font_size=fs_sm)
    plotlyFigure.update_xaxes(title_font_size=fs_sm, tickfont_size=fs_sm)
    plotlyFigure.update_yaxes(title_font_size=fs_sm, tickfont_size=fs_sm)
    plotlyFigure.update_annotations(font_size=fs_sm)

    # subplot labels
    if subfigName not in ['fig6']:
        numSubPlots = __countNumbSubplots(plotlyFigure)
        for i in range(numSubPlots):
            subfigLabel = subfigName[-1] if subfigName[-1] in ascii_lowercase else ascii_lowercase[i]
            plotlyFigure.add_annotation(
                showarrow=False,
                text=f"<b>{subfigLabel}</b>",
                font_size=fs_lg,
                x=0.0,
                xanchor='left',
                xref=f"x{i+1 if i else ''} domain",
                y=1.0,
                yanchor='bottom',
                yref=f"y{i+1 if i else ''} domain",
                yshift=10.0,
            )


def __countNumbSubplots(figure: go.Figure):
    return sum(1 for row in range(len(figure._grid_ref))
                 for col in range(len(figure._grid_ref[row]))
                 if figure._grid_ref[row][col] is not None) \
                 if figure._grid_ref is not None else 1
