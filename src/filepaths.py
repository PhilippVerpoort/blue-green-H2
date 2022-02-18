import pathlib


BASE_PATH = pathlib.Path(__file__).parent.parent.resolve()
ASSETS_PATH = BASE_PATH.joinpath("assets").resolve()
INPUT_PATH = BASE_PATH.joinpath("input").resolve()
OUTPUT_PATH = BASE_PATH.joinpath("output").resolve()

def getFilePath(dname, fname):
    return BASE_PATH.joinpath(dname).joinpath(fname).resolve()

def getFilePathAssets(fname):
    return ASSETS_PATH.joinpath(fname).resolve()

def getFilePathInput(fname):
    return INPUT_PATH.joinpath(fname).resolve()

def getFilePathOutput(fname):
    return OUTPUT_PATH.joinpath(fname).resolve()
