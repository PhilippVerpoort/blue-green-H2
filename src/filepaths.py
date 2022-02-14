import os

pwd = os.path.join(os.path.dirname(__file__), '..')

def getFilePath(dname, fname):
    return os.path.join(pwd, dname, fname)

def getFilePathAssets(fname):
    return getFilePath('assets/', fname)

def getFilePathInput(fname):
    return getFilePath('input/', fname)

def getFilePathOutput(fname):
    return getFilePath('output/', fname)
