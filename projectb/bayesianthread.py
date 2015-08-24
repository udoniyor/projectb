"""
The bayesian optimization module for the Graphical User Interface. Parts of the module
borrow code from pybo by Matthew W. Hoffman and Bobak Shahriari. The module takes in
parameters list, processes the file and proceeds with specified Bayesian Optimization
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
# update a recarray at the end of solve_bayesopt.

import numpy as np
from sets import Set
import pygp
import inspect
import functools
import time
import CGOModel from projectb.objwrapper

# update a recarray at the end of solve_bayesopt.
from mwhutils.random import rstate

# each method/class defined exported by these modules will be exposed as a
# string to the solve_bayesopt method so that we can swap in/out different
# components for the "meta" solver.
from pybo.bayesopt import inits
from pybo.bayesopt import solvers
from pybo.bayesopt import policies
from pybo.bayesopt import recommenders


# The Bayesian optimization class, requires parameters and pipes
# to communicate with another process. Thus allowing spawing the
# module to another process.
class BayesianOptProcess():
    def __init__(self, params, pipein, pipeout):
        self.params = params
        self.experiments = []
        self.models = []
        self.pipein = pipein
        self.stop = False
        self.pipeout = pipeout
        self.outputdir = "" if self.params["outputdir"] == "Output Directory" else self.params["outputdir"]
        self.console = lambda t,v=2: pipeout.send({"console": {"text":t,"verbose":v}})

        # Create an objective function from the parameters
        modelfunc = CGOModel(
            command=params["command"],
            inputURI=params["modelinput"],
            outputURI=params["modeloutput"],
            bounds=params["bounds"],
            console=self.console,
            normalize=bool(params["normalize"]),
            minmax=1 if params["objective"] == "max" else -1
        )

        # Shortcut to setup the policies
        policyshortcut = {
            "ei": ("ei", {"xi": float(self.params["eixi"])}),
            "pi": ("pi", {"xi": float(self.params["pixi"])}),
            "ucb": ("ucb", {"delta": float(self.params["ucbdelta"]), "xi": float(self.params["ucbxi"])}),
            "thompson": ("thompson", {"n": float(self.params["thompsonn"]), "rng": float(self.params["thompsonrng"])}),
        }

        # create list of experiments to be performed
        for p in params["policies"]:
            for k in params["kernels"]:
                kwargs = {
                    "objective": modelfunc,
                    "bounds": np.array(params["bounds"]),
                    "niter": int(float(params["iter"])),
                    "init": params["initializer"],
                    "policy": policyshortcut[p],
                    "kernel": k,
                    "solver": params["solver"],
                    "recommender": params["recommender"],
                }
                self.experiments.append(kwargs)
        self.run()

    # Go through all experiments and always check if we need to stop
    # and update the observer on what is happening via the pipes
    def run(self):
        for i, e in enumerate(self.experiments):
            start = time.clock()
            if self.pipeout.poll():
                o = self.pipeout.recv()
                if o.has_key("stop"):
                    self.stop = o["stop"]

            if self.stop:
                break
            self.pipeout.send({
                "expnum": (str(i + 1) + "/" + str(len(self.experiments))),
                "policy": e["policy"][0],
                "kernel": e["kernel"]
            })

            if self.params["dimscheudler"]:
                e.update({"dims": int(self.params["dims"])})
                m = self.solve_bayesopt_dim(**e)
            else:
                m = self.solve_bayesopt(**e)
            self.models.append(m)
            del e["objective"]
            e.update({"iterfinish": m["iterfinish"], "best": np.max(m["model"].data[1]), "time": time.clock() - start,
                      "modelid": i})
        self.console("Ended Bayesian Optimization")
        self.console("Now you can interact with the model(s)")
        self.pipeout.send({"stopped_bayes": self.experiments})

        # Once done, listen for any queries from the observer module
        while True:
            if self.pipeout.poll():
                output = self.pipeout.recv()
                if output.has_key("stop_posterior_connector"):
                    break
                if output.has_key("posterior"):
                    self.writeposterior(output["posterior"], output["modelid"])

    # For a given module id and file with X points, write the mu and var
    # to the default output directory
    def writeposterior(self, file, modelid):
        try:
            data = np.genfromtxt(file, dtype=float, delimiter=',')
            model = self.models[modelid]["model"]
            e = self.experiments[modelid]
            mu, var = model.posterior(data)[:2]
            filename = self.outputdir + "_".join([e["policy"][0], e["kernel"], str(e["niter"])])
            with open(filename, "a+") as f:
                for i, d in enumerate(data):
                    f.write("0,Query," + str(mu[i]) + "," + str(var[i]) + "," + ",".join(str(a) for a in d) + "\n")
            self.console("The query file was successfully processed")
        except:
            self.console("The specified file does not conform to the required file format to query the model")

    # The Bayesian Optimization Solver
    def solve_bayesopt(self,
                       objective,
                       bounds,
                       kernel="se",
                       niter=150,
                       init='sobol',
                       policy='ei',
                       solver='direct',
                       recommender='latent'):
        """
        The following part, borrows some code from the pybo code.
        Therefore, retains a similar structure and parameters.

        From Pybo:
            Maximize the given function using Bayesian Optimization.
            Args:
                objective: function handle representing the objective function.
                bounds: bounds of the search space as a (d,2)-array.
                niter: horizon for optimization.
                init: the initialization component.
                policy: the acquisition component.
                solver: the inner-loop solver component.
                recommender: the recommendation component.

            Note that the modular way in which this function has been written allows
            one to also pass parameters directly to some of the components. This works
            for the `init`, `policy`, `solver`, and `recommender` inputs. These
            components can be passed as either a string, a function, or a 2-tuple where
            the first item is a string/function and the second is a dictionary of
            additional arguments to pass to the component.
            Returns:
               A dictionary with the model, recommended values, and finished iteration
            """
        filename = self.outputdir + "_".join([policy[0], kernel, str(niter)])
        bounds = np.array(bounds, dtype=float, ndmin=2)
        rng = rstate(None)
        # get the model components.
        init, policy, solver, recommender = \
            self.get_components(init, policy, solver, recommender, rng)
        # Create the model with the data
        model = self.initialmodel(objective, init, bounds, kernel)
        # Write the initial data to a file
        with open(filename, "a+") as f:
            for i, y in enumerate(model.data[1]):
                f.write("0," + str(y) + ",0,0," + ",".join([str(a) for a in model.data[0][i]]) + "\n")
        # Send data to the observer
        self.pipeout.send({"inidata": {"x": model.data[0].tolist(), "y": model.data[1].tolist()}})
        self.console("Starting Bayesian Optimization")
        # Start BayesOpt
        for i in xrange(model.ndata, niter):
            # Record current time and iteration
            start = time.clock()
            curiter = i
            # Check if Observer has terminated the process
            if self.pipeout.poll():
                o = self.pipeout.recv()
                if o.has_key("stop"):
                    self.stop = o["stop"]
            if self.stop:
                break
            # get the next point to evaluate.
            index = policy(model)
            x, _ = solver(index, bounds)
            glomu, glovar = model.posterior(x, grad=False)[:2]
            # make an observation and record it.
            y = objective(x)
            model.add_data(x, y)
            # Send out the data to the observer and write to the file
            interval = time.clock() - start
            with open(filename, "a+") as f:
                f.write(str(interval) + "," + str(y) + "," + str(glomu[0]) + "," + str(glovar[0]) + ",".join(
                    [str(a) for a in x]) + "\n")
            self.pipeout.send({"data": {"y": y, "x": x, "mu": glomu[0], "var": glovar[0], "time": interval}})
        # Get the recommender point from the model
        recx = recommender(model, bounds)
        recmu, recvar = model.posterior(recx, grad=False)[:2]
        with open(filename, "a+") as f:
            f.write("0,Rec.," + str(recmu[0]) + "," + str(recvar[0]) + "," + ",".join([str(s) for s in recx]) + "\n")
        self.console("Finished experiment")
        return {"model": model, "iterfinish": curiter, "rec": {"x": recx, "mu": recmu, "var": recvar}}

    # The Bayesian Optimization Solver with Dimension Scheduler
    def solve_bayesopt_dim(self,
                           objective,
                           bounds,
                           kernel="se",
                           niter=150,
                           dims=2,
                           init='sobol',
                           policy='ei',
                           solver='direct',
                           recommender='latent'):
        """
        The following part, borrows some code from the pybo code.
        Therefore, retains a similar structure and parameters.

        From Pybo (with updates):
            Maximize the given function using Bayesian Optimization.
            Args:
                objective: function handle representing the objective function.
                bounds: bounds of the search space as a (d,2)-array.
                niter: horizon for optimization.
                dims: number of dimensions per permutation
                init: the initialization component.
                policy: the acquisition component.
                solver: the inner-loop solver component.
                recommender: the recommendation component.

            Note that the modular way in which this function has been written allows
            one to also pass parameters directly to some of the components. This works
            for the `init`, `policy`, `solver`, and `recommender` inputs. These
            components can be passed as either a string, a function, or a 2-tuple where
            the first item is a string/function and the second is a dictionary of
            additional arguments to pass to the component.
            Returns:
               Nothing, everything is written to a file
        """

        filename = self.outputdir + "_".join([policy[0], kernel, str(niter)])
        bounds = np.array(bounds, dtype=float, ndmin=2)
        # initialize the random number generator.
        rng = rstate(None)
        # get the model components.
        init, policy, solver, recommender = \
            self.get_components(init, policy, solver, recommender, rng)
        # Create the model with the data
        model = self.initialmodel(objective, init, bounds, kernel)
        with open(filename, "a+") as f:
            for i, y in enumerate(model.data[1]):
                f.write("0," + str(y) + ",0,0," + ",".join([str(a) for a in model.data[0][i]]) + "\n")
        # Send data to the observer
        self.pipeout.send({"inidata": {"x": model.data[0].tolist(), "y": model.data[1].tolist()}})
        # Set up Dimension Scheduler Dictionaries
        modelsDict = {}
        dimDict = {}
        bY = np.argmax(model.data[1])
        bX = model.data[0][bY]
        objective.set_initial(bX)
        objective.set_best(model.data[1][bY])
        dimensionsProb = [0.1] * len(bounds)
        self.console("Starting Bayesian Optimization")
        for i in xrange(model.ndata, niter):
            start = time.clock()
            curiter = i
            if self.pipeout.poll():
                o = self.pipeout.recv()
                if o.has_key("stop"):
                    self.stop = o["stop"]
            if self.stop:
                break
            # Update the probabilities
            if (i % 50 == 0):
                mydata = model.data[0]
                mu = mydata.mean(axis=0)
                sigma = mydata.std(axis=0)
                a = (mydata - mu) / sigma
                C = np.cov(a.T)
                evals, evecs = np.linalg.eig(C)
                vars = evals / float(len(evals))
                dimensionsProb = vars / vars.sum()

            # generate new dimension and update the bounds and set the dimensions on the objective
            d = self.getRandomDimensions(dimensionsProb, dims)
            objective.set_dimensions(d)
            boundslowerdim = objective.get_bounds()
            # check if the model exists, else create a new one
            if not modelsDict.has_key(str(d)):
                tX = self.getInputsDimRed(model, d)
                tY = model.data[1]
                m = self.createNewModel(tX, tY, boundslowerdim, kernel)
                m.add_data(tX, tY)
                modelsDict[str(d)] = m
                dimDict[str(d)] = d
            # get model for current dimensions
            modellowerdim = modelsDict.get(str(d))

            # get the next point to evaluate.
            index = policy(modellowerdim)

            x, _ = solver(index, boundslowerdim)

            # make an observation and record it.
            y = objective(x)
            curX = objective.get_prev_input()
            glomu, glovar = model.posterior(curX, grad=False)[:2]
            # Send out the data to the observer

            model.add_data(curX, y)
            modellowerdim.add_data(x, y)
            interval = time.clock() - start
            with open(filename, "a+") as f:
                f.write(str(interval) + "," + str(y) + "," + str(glomu[0]) + "," + str(glovar[0]) + ",".join(
                    [str(a) for a in curX]) + "\n")
            self.pipeout.send({"data": {"y": y, "x": curX, "mu": glomu[0], "var": glovar[0], "time": interval}})
            if objective.get_best() is not None:
                if (y > objective.get_best()):
                    objective.set_best(y)
                    objective.change_initial(x)
            else:
                objective.set_best(y)
                objective.change_initial(x)
        # Get the recommender point from the model
        recx = recommender(model, bounds)
        recmu, recvar = model.posterior(recx, grad=False)[:2]
        with open(filename, "a+") as f:
            f.write("0,Rec.," + str(recmu) + "," + str(recvar) + "," + ",".join([str(s) for s in recx]) + "\n")
        self.console("Finished experiment")
        return {"model": model, "iterfinish": curiter, "rec": {"x": recx, "mu": recmu, "var": recvar}}

    # Takes out data from the model only for the specified dimensions
    def getInputsDimRed(self, model, dimensions):
        data = model.data[0]
        stackedData = np.array(data[:, dimensions[0]])
        for d in xrange(1, len(dimensions)):
            stackedData = np.column_stack((stackedData, data[:, dimensions[d]]))
        return stackedData

    # Creates a model from given parameters
    # The variables are set from the user specified commands
    def createNewModel(self, X, Y, bounds, kernel):
        # initialize parameters of a simple GP model.
        sf = eval(self.params["gpsf"])
        mu = eval(self.params["gpmu"])
        ell = eval(self.params["gpell"])
        sn = eval(self.params["gpsn"])
        # specify a hyperprior for the GP.
        prior = {
            'sn': (pygp.priors.Horseshoe(scale=eval(self.params["priorsnscale"]), min=eval(self.params["priorsnmin"]))),
            'sf': pygp.priors.LogNormal(mu=eval(self.params["priorsfmu"]), sigma=eval(self.params["priorsfsigma"]),
                                        min=eval(self.params["priorsfmin"])),
            'ell': pygp.priors.Uniform(eval(self.params["priorella"]), eval(self.params["priorellb"])),
            'mu': pygp.priors.Gaussian(eval(self.params["priormumu"]), eval(self.params["priormuvar"]))}

        # create the GP model (with hyperprior).
        model = pygp.BasicGP(sn, sf, ell, mu, kernel=kernel)
        model = pygp.meta.MCMC(model, prior, n=int(self.params["mcmcn"]), burn=int(self.params["mcmcburn"]))
        return model

    # Creates a model from specified parameters, bootstrapped with data if provided
    def initialmodel(self, objective, init, bounds, kernel):
        n = 30
        X = []
        Y = []
        data = [[], []]
        if len(self.params["data"][0]) > 0:
            data = self.params["data"]
        try:
            n = int(self.params["initializernum"])
        except:
            self.console("The initial number of samples must be a number")
        if n > 0:
            self.console("Starting initializer")
            X = init(bounds, n=n)
            Y = [objective(x) for x in X]
            self.console("Finished initializer")
        elif data == [[], []]:
            self.console("You must provide data or have more than zero N initial points to sample")
            ValueError(("You must provide data or have more than zero N initial points to sample"))

        allX = np.concatenate((data[0], X), axis=0) if len(data[0]) > 0 else X
        allY = np.concatenate((data[1], Y), axis=0) if len(data[1]) > 0 else Y

        self.console("Creating a model")
        m = self.createNewModel(allX, allY, bounds, kernel)
        self.console("Adding init data to the model")
        m.add_data(allX, allY)
        return m

    # Returns a n random dimension from a probability dist. provided
    def getRandomDimensions(self, dimensionProbabilities, numberOfDimensions):
        cumulativeDP = np.array(dimensionProbabilities).cumsum()

        def randomDimensions(dimensionProbabilities):
            index = 0
            random = np.random.random_sample()
            while cumulativeDP[index] <= random:
                index = index + 1
            return index

        def checksAndBalances():
            ranD = [randomDimensions(dimensionProbabilities) for a in xrange(0, numberOfDimensions)]
            if not (len(Set(ranD)) == numberOfDimensions):
                return checksAndBalances()
            else:
                ranD.sort()
                return ranD

        return checksAndBalances()

    # Get random dimensions permutation
    def getPermutationsDim(self, dims, sizes):
        return np.random.permutation(np.arange(dims)).reshape(sizes)

    # The following function is copied from pybo, used to get all the components.
    def get_components(self, init, policy, solver, recommender, rng):
        """
        Return model components for Bayesian optimization of the correct form given
        string identifiers.
        """

        def get_func(key, value, module, lstrip):
            """
            Construct the model component if the given value is either a function
            or a string identifying a function in the given module (after stripping
            extraneous text). The value can also be passed as a 2-tuple where the
            second element includes kwargs. Partially apply any kwargs and the rng
            before returning the function.
            """
            if isinstance(value, (list, tuple)):
                try:
                    value, kwargs = value
                    kwargs = dict(kwargs)
                except (ValueError, TypeError):
                    raise ValueError('invalid arguments for component %r' % key)
            else:
                kwargs = {}

            if hasattr(value, '__call__'):
                func = value
            else:
                for fname in module.__all__:
                    func = getattr(module, fname)
                    if fname.startswith(lstrip):
                        fname = fname[len(lstrip):]
                    fname = fname.lower()
                    if fname == value:
                        break
                else:
                    raise ValueError('invalid identifier for component %r' % key)

            kwarg_set = set(kwargs.keys())
            valid_set = getattr(func, '_params', set())

            if not kwarg_set.issubset(valid_set):
                raise ValueError('unknown parameters for component %r: %r' %
                                 (key, list(kwarg_set - valid_set)))

            if 'rng' in inspect.getargspec(func).args:
                kwargs['rng'] = rng

            if len(kwargs) > 0:
                func = functools.partial(func, **kwargs)

            return func

        return (get_func('init', init, inits, lstrip='init_'),
                get_func('policy', policy, policies, lstrip=''),
                get_func('solver', solver, solvers, lstrip='solve_'),
                get_func('recommender', recommender, recommenders, lstrip='best_'))
