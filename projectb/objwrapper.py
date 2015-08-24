import os
import numpy as np
import subprocess


# Class to transform commands, input and output data into a callable object
class CMDToPython:
    def __init__(self, command, inputURI, outputURI, console=None):
        self.FNULL = open(os.devnull, 'w')
        self.command = command.split(" ")
        self.inputLocation = inputURI
        self.outputLocation = outputURI
        self.console = console

    # Set parameters for the Scilab Model
    def setInputParameters(self, parametersList):
        inputFile = open(self.inputLocation, "w")
        for i in xrange(len(parametersList)):
            inputFile.write(str(parametersList[i]) + "\n")
        inputFile.close()

    # Get the output of the simulation
    def getOutput(self):
        outputFile = open(self.outputLocation, "r")
        output = outputFile.read()
        outputFile.close()
        return np.array([float(output)])

    # Run the simulation
    def runSimulation(self):
        out = subprocess.check_output(self.command)
        if self.console is not None:
            for o in out.split("\n"):
                if o is not "":
                    self.console(o, 2)

    # Given parameters get the output of the External Model
    def objective(self, paramList):
        self.setInputParameters(paramList)
        self.runSimulation()
        return self.getOutput()


"""
 The following module is based on the Global Optimization Model by pybo, but with support
 for Dimension Scheduler and normalization of the data, and ability to choose between
 maximization and minimization.
"""


class CGOModel(object):
    def __init__(self, command, inputURI, outputURI, bounds, console=None, normalize=False, minmax=1):
        self.objectiveF = CMDToPython(command, inputURI, outputURI, console)
        self.normalize = normalize
        self.bounds = bounds
        self.boundsS = bounds
        self.dimensions = [x for x in xrange(len(bounds))]
        self.reset_bounds(self.dimensions)
        self.initial = [0] * (len(bounds))
        self.prev_input = [0] * (len(bounds))
        self.best = None
        self.minmax = minmax

    # Returns current bounds
    def get_bounds(self):
        return np.array(self.bounds)

    # Returns best value achieved so far
    def get_best(self):
        return self.best

    # Set the best value achieved
    def set_best(self, best):
        self.best = best

    # Fix all other dimensions to the best value parameters, except specified dimensions
    def set_dimensions(self, d):
        self.dimensions = d
        self.reset_bounds(d)

    # Update the bounds to the given dimension
    def reset_bounds(self, dimensions):
        if self.normalize:
            self.bounds = [[0., 1.]] * len(self.dimensions)
        else:
            self.bounds = []
            for x in dimensions:
                self.bounds.append(self.boundsS[x])

    # Set the arg max/min
    def set_initial(self, x):
        self.initial = x

    # Update arg max/min so far
    def change_initial(self, x):
        input = list(self.initial)
        for d in xrange(len(self.dimensions)):
            input[(self.dimensions[d])] = x[d]
        self.initial = input

    # Get arg max/min
    def get_initial(self):
        return self.initial

    # Get previous input data
    def get_prev_input(self):
        return self.prev_input

    # Default call
    def __call__(self, x):
        return self.get(x)[0]

    # Get output of the function given the input
    def get(self, x):
        input = list(self.initial)
        for d in xrange(len(self.dimensions)):
            input[(self.dimensions[d])] = x[d]
        self.prev_input = input
        if (self.normalize):
            for i, j in enumerate(input):
                input[i] = j * self.boundsS[i][1]
        y = self.objectiveF.objective(input)
        return self.minmax * y
