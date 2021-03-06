from src.config_load import figure_print
from src.filepaths import getFilePathOutput
from src.plotting.styling.print import getImageSize, addPrintSpecificStyling


def exportFigsToFiles(figs: dict):
    addPrintSpecificStyling(figs)

    print('Exporting to files...')

    for subfigName, plotlyFigure in figs.items():
        if plotlyFigure is None: continue

        w_mm, h_mm = figure_print[subfigName]['size']

        print(f"Exporting {subfigName}...")

        plotlyFigure.write_image(getFilePathOutput(f"{subfigName}.png"), **getImageSize(w_mm, h_mm))
