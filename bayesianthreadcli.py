from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
# update a recarray at the end of solve_bayesopt.
from numpy.lib.recfunctions import append_fields
from mwhutils.random import rstate

import pygp
import numpy as np
from sets import Set
import pygp
import inspect
import functools

# update a recarray at the end of solve_bayesopt.
from numpy.lib.recfunctions import append_fields
from mwhutils.random import rstate

# each method/class defined exported by these modules will be exposed as a
# string to the solve_bayesopt method so that we can swap in/out different
# components for the "meta" solver.
from pybo.bayesopt import inits
from pybo.bayesopt import solvers
from pybo.bayesopt import policies
from pybo.bayesopt import recommenders

import objwrapper
from multiprocessing import Process, Pipe
import threading

class BayesianOptProcess():
    def __init__(self, params, console):
        self.params = params
        self.experiments = []
        self.console = console

        modelfunc = objwrapper.CGOModel(
            command=params["command"],
            inputURI=params["modelinput"],
            outputURI=params["modeloutput"],
            bounds=params["bounds"],
            console=None,
            normalize=bool(params["normalize"]),
            minmax=1 if params["objective"] == "max" else -1
        )

        policyshortcut = {
            "ei": ("ei", {"xi": float(self.params["eixi"])}),
            "pi": ("pi", {"xi": float(self.params["pixi"])}),
            "ucb": ("ucb", {"delta": float(self.params["ucbdelta"]), "xi": float(self.params["ucbxi"])}),
            "thompson": ("thompson", {"n": float(self.params["thompsonn"]), "rng": float(self.params["thompsonrng"])}),
        }

        for p in params["policies"]:
            for k in params["kernels"]:
                kwargs = {
                    "objective": modelfunc,
                    "bounds": np.array(params["bounds"]),
                    "niter": int(float(params["iter"])),
                    "init": params["init"],
                    "policy": policyshortcut[p],
                    "kernel": k,
                    "solver": params["solver"],
                    "recommender": params["recommender"],
                }
                self.experiments.append(kwargs)
        self.run()

    def run(self):
        for i, e in enumerate(self.experiments):
            self.console("Starting with "+e["policy"][0] + " and "+e["kernel"]+" kernel.")
            if bool(int(self.params["dimscheudler"])):
                e.update({"dims": int(self.params["dims"])})
                self.solve_bayesopt_dim(**e)
            else:
                self.solve_bayesopt(**e)
        self.console("Ended Bayesian Optimization")

    def getInputsDimRed(self, model, dims):
        data = model.data[0]
        stackedData = np.array(data[:, dims[0]])
        for d in xrange(1, len(dims)):
            stackedData = np.column_stack((stackedData, data[:, dims[d]]))
        return stackedData

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

    def getPermutationsDim(self, dims, sizes):
        return np.random.permutation(np.arange(dims)).reshape(sizes)

    def solve_bayesopt(self,
                       objective,
                       bounds,
                       kernel="se",
                       niter=150,
                       init='sobol',
                       policy='ei',
                       solver='direct',
                       recommender='latent',
                       callback=None):

        bounds = np.array(bounds, dtype=float, ndmin=2)
        # initialize the random number generator.
        rng = rstate(None)
        # get the model components.
        init, policy, solver, recommender = \
            self.get_components(init, policy, solver, recommender, rng)
        self.console("Starting initializer")
        # create a list of initial points to query.
        X = init(bounds, n=5)
        Y = [objective(x) for x in X]

        self.console("Finished initializer")
        self.console("Creating a model")
        model = self.createNewModel(X, Y, bounds, kernel)
        self.console("Adding init data to the model")
        # add any initial data to our model.
        model.add_data(X, Y)

        # allocate a datastructure containing "convergence" info.
        info = np.zeros(niter, [('x', np.float, (len(bounds),)),
                                ('y', np.float),
                                ('xbest', np.float, (len(bounds),))])
        # initialize the data.
        info['x'][:len(X)] = X
        info['y'][:len(Y)] = Y
        info['xbest'][:len(Y)] = [X[np.argmax(Y[:i + 1])] for i in xrange(len(Y))]
        self.console("Starting Bayesian Optimization")
        for i in xrange(model.ndata, niter):
            # get the next point to evaluate.
            index = policy(model)
            x, _ = solver(index, bounds)
            glomu, glovar = model.posterior(x, grad=False)[:2]
            # make an observation and record it.
            y = objective(x)
            # Send out the data to the observer
            model.add_data(x, y)
            # record everything.
            info[i] = (x, y, recommender(model, bounds))


    def solve_bayesopt_dim(self,
                           objective,
                           bounds,
                           kernel="se",
                           dims=2,
                           niter=150,
                           init='sobol',
                           policy='ei',
                           solver='direct',
                           recommender='latent',
                           callback=None):

        # make sure the bounds are a 2d-array.
        bounds = np.array(bounds, dtype=float, ndmin=2)

        # initialize the random number generator.
        rng = rstate(None)

        # get the model components.
        init, policy, solver, recommender = \
            self.get_components(init, policy, solver, recommender, rng)
        self.console("Starting the initializer")
        X = init(bounds, n=30)
        Y = [objective(x) for x in X]

        self.console("Finished initializer")
        self.console("Creating a model")
        model = self.createNewModel(X, Y, bounds, kernel)
        self.console("Adding init data to the model")
        # add any initial data to our model.
        model.add_data(X, Y)

        # allocate a datastructure containing "convergence" info.
        info = np.zeros(niter, [('x', np.float, (len(bounds),)),
                                ('y', np.float),
                                ('xbest', np.float, (len(bounds),))])

        # initialize the data.
        info['x'][:len(X)] = X
        info['y'][:len(Y)] = Y
        info['xbest'][:len(Y)] = [X[np.argmax(Y[:i + 1])] for i in xrange(len(Y))]

        modelsDict = {}
        dimDict = {}
        bY = np.argmax(info["y"][:30])
        bX = info["x"][bY]
        objective.set_initial(bX)
        objective.set_best(info["y"][bY])
        self.console("Starting Bayesian Optimization")
        dimensionsProb = [0.1] * len(bounds)
        for i in xrange(model.ndata, niter):
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
            boundsd = objective.get_bounds()
            # check if the model exists, else create a new one
            if not modelsDict.has_key(str(d)):
                tX = self.getInputsDimRed(model, d)
                tY = model.data[1]
                m = self.createNewModel(tX, tY, boundsd, kernel)
                m.add_data(tX, tY)
                modelsDict[str(d)] = m
                dimDict[str(d)] = d
            # get model for current dimensions
            modelD = modelsDict.get(str(d))

            # get the next point to evaluate.
            index = policy(modelD)
            x, _ = solver(index, boundsd)


            # make an observation and record it.
            y = objective(x)
            curX = objective.get_prev_input()
            glomu, glovar = model.posterior(curX, grad=False)[:2]

            # Add the new data to the models
            model.add_data(curX, y)
            modelD.add_data(x, y)

            info[i] = (curX, y, recommender(model, bounds))

            # update the initial
            if objective.get_best() is not None:
                if (y > objective.get_best()):
                    objective.set_best(y)
                    objective.change_initial(x)
            else:
                objective.set_best(y)
                objective.change_initial(x)

        self.console("Finished the experiment")


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
