import os

pwd = os.getcwd()

def getFilePath(dname, fname):
    return os.path.join(pwd, dname, fname)

def getFilePathAssets(fname):
    return getFilePath('assets/', fname)

def getFilePathInputs(fname):
    return getFilePath('input/', fname)
