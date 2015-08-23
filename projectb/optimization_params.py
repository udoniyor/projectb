__author__ = 'doniy'
from Tkinter import StringVar, IntVar

class OptimizationParams(object):
    def __init__(self,file=None):
        self.params = {
            "command": None,
            "modelURI": None,
            "modelInput": None,
            "modelOutput": None,
            "bounds":None,
            "resultsOutput": None,
            "policies":["ei"],
            "kernels":["matern5"],
            "iter":150,
            "objective": 1
        }

        if file is not None:
            self.parseFile(file)

    def parseFile(self,file):
        return False

    def getParam(self,p):
        return self.params[p]

    def setParam(self,p,s):
        self.params[p]=s

    def getParamV(self,p):
        return self.params[p]

    def ready(self):
        for p in self.params:
            if p is None:
                return False
        return True

