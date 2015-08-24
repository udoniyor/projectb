import numpy as np
import os

"""
    All the necessary functions to parse in, out and update the variable parameters.
"""


# Parse a file into a list
def parsein(file, params, console=None):
    def add_data(d):
        try:
            y = float[d[1]]
            x = float(d[4:])
            param["data"][0].append(x)
            param["data"][1].append(y)
        except:
            # This assuming anything that does not convert is either Recommended value or from Posterior Calculation
            pass

    policies = set(["ei", "pi", "thompson", "ucb"])
    kernels = set(["matern1", "matern3", "matern5", "se"])
    objectives = set(["max", "min"])
    solvers = set(["lbfgs", "direct"])
    recommenders = set(["incumbent", "latent", "observed"])
    initializers = set(["latin", "sobol", "uniform"])
    boundseen = False
    paramsfloats = ["eixi", "pixi", "ucbdelta", "ucbxi", "thompsonn", "thompsonrng"]
    paramsint = ["dims", "iter", "mcmcburn", "mcmcn"]
    booleanparams = ["normalize", "dimscheudler"]
    with open(file, "r") as f:
        for line in f:
            splitline = line.replace("\n", "").split(",")
            param = splitline[0].lower()
            if param != "":
                if (params.has_key(param)):
                    if param in booleanparams:
                        try:
                            params[param] = bool(splitline[1])
                        except:
                            if console is not None:
                                console.log("The " + param + " must be a boolean, please check the file")
                            else:
                                raise ValueError(("The " + param + " does must be a boolean, please check the file"))
                    if param == "bounds":
                        try:
                            if not boundseen:
                                params["bounds"][:] = []
                            boundseen = True
                            params["bounds"].append([float(splitline[1]), float(splitline[2])])
                        except:
                            if console is not None:
                                console.log("The bound values are not numbers, please check the file")
                            else:
                                raise ValueError(("The bound values are not numbers, please check the file"))
                    elif (param == "objective"):
                        if splitline[1] in objectives:
                            params[param] = splitline[1]
                        else:
                            if console is not None:
                                console.log("The objective " + splitline[1] + " does not exist, please check the file")
                            else:
                                raise ValueError(
                                    ("The objective " + splitline[1] + " does not exist, please check the file"))
                    elif (param == "solver"):
                        if splitline[1] in solvers:
                            params[param] = splitline[1]
                        else:
                            if console is not None:
                                console.log("The solver " + splitline[1] + " does not exist, please check the file")
                            else:
                                raise ValueError(("The solver " + splitline[1] + " does not exist, please check the file"))
                    elif (param == "initializer"):
                        if splitline[1] in initializers:
                            params[param] = splitline[1]
                        else:
                            if console is not None:
                                console.log("The initializer " + splitline[1] + " does not exist, please check the file")
                            else:
                                raise ValueError(
                                    ("The initializer " + splitline[1] + " does not exist, please check the file"))
                    elif (param == "recommender"):
                        if splitline[1] in recommenders:
                            params[param] = splitline[1]
                        else:
                            if console is not None:
                                console.log("The recommender " + splitline[1] + " does not exist, please check the file")
                            else:
                                raise ValueError(
                                    ("The recommender " + splitline[1] + " does not exist, please check the file"))
                    elif (param == "policies"):
                        for policy in splitline[1:]:
                            if policy in policies:
                                params[param].append(policy)
                            else:
                                if console is not None:
                                    console.log("The policy values " + policy + " does not exist, please check the file")
                                else:
                                    raise ValueError(
                                        ("The policy values " + policy + " does not exist, please check the file"))
                    elif (param == "kernels"):
                        for kernel in splitline[1:]:
                            if kernel in kernels:
                                params[param].append(kernel)
                            else:
                                if console is not None:
                                    console.log("The kernel values " + kernel + " does not exist, please check the file")
                                else:
                                    raise ValueError(
                                        ("The kernel values " + kernel + " does not exist, please check the file"))
                    elif (param == "data"):
                        params["data"] = [[], []]
                        if splitline[1] is not None:
                            if os.path.isfile(splitline[1]):
                                with open(splitline[1], "r") as datafile:
                                    for x in datafile:
                                        add_data(np.fromstring(line, dtype=float, sep=','))
                            else:
                                if console is not None:
                                    console.log("The " + splitline[1] + " data file does not exists, check the file URI")
                                else:
                                    raise ValueError(
                                        "The " + splitline[1] + " data file does not exists, check the file URI")

                        else:
                            break;
                    else:
                        if param in paramsfloats:
                            try:
                                params[param] = float(splitline[1])
                            except:
                                ValueError(('The parameter ' + param + " must be a float"))
                        elif param in paramsint:
                            try:
                                params[param] = int(float(splitline[1]))
                            except:
                                ValueError(('The parameter ' + param + " must be an interger"))
                        else:
                            params[param] = ",".join(splitline[1:])
                else:
                    raise ValueError(
                        ('The parameter ' + param + " does not exists, please check the parameter name syntax"))

        for line in f:
            add_data(np.fromstring(line, dtype=float, sep=','))

    return params


# Parse  Var (Tk Type) List into a simple list
def parseintosimple(customvarparms):
    kernels = {3: "matern1", 2: "matern3", 1: "matern5", 0: "se"}
    policies = {0: "ei", 1: "pi", 3: "thompson", 2: "ucb"}

    def flattenparam(key, value):
        if key == "policies":
            return filter(None, [v if value[k].get() else None for (k, v) in policies.items()])
        elif key == "kernels":
            return filter(None, [v if value[k].get() else None for (k, v) in kernels.items()])
        elif key == "bounds":
            return value
        elif key == "normalize" or key == "dimscheudler":
            return True if value == 1 else False
        elif key == "data":
            data = [[], []]
            if os.path.isfile(value.get()):
                with open(value.get(), "r") as f:
                    for d in f:
                        try:
                            y = float[d[0]]
                            x = float(d[3:])
                            data[0].append(x)
                            data[1].append(y)
                        except:
                            # This assuming anything that does not convert is either Recommended value or from Posterior Calculation
                            pass
            return data
        else:
            return value.get()

    return dict((k, flattenparam(k, v)) for (k, v) in customvarparms.items())


# Update Var (Tk Type) list from a simple list
def parsemodifycustomvar(customvarsparam, simpleparams):
    kernels = {3: "matern1", 2: "matern3", 1: "matern5", 0: "se"}
    policies = {0: "ei", 1: "pi", 3: "thompson", 2: "ucb"}
    for (key, value) in customvarsparam.items():
        if key == "policies":
            for i, p in enumerate(value):
                p.set(1) if policies[i] in simpleparams[key] else p.set(0)
        elif key == "kernels":
            for i, k in enumerate(value):
                k.set(1) if kernels[i] in simpleparams[key] else k.set(0)
        elif key == "bounds":
            customvarsparam[key] = simpleparams[key]
        elif key == "data":
            if type(value) == str:
                customvarsparam[key].set(value)
            else:
                customvarsparam[key] = value
        elif key == "normalize" or key == "dimscheudler":
            if simpleparams[key] == "True":
                customvarsparam[key].set(1)
            else:
                customvarsparam[key].set(0)

        else:
            customvarsparam[key].set(simpleparams[key])


# Parse out the parameters list
def parseout(file, param, console=None):
    defaultparams = {
        "command": " i.e. python C://Users/Desktop/model/final4.py",
        "modelinput": "Select Input File",
        "modeloutput": "Select Output File",
        "bounds": [],
        "outputdir": "Output Directory",
        "solver": "direct",
        "initializer": "sobol",
        "initializernum": 30,
        "recommender": "latent",
        "normalize": False,
        "data": "Select Data File",
        "dims": 2.,
        "dimscheudler": False,
        "gpsf": "np.std(Y)",
        "gpmu": "np.mean(Y)",
        "gpell": "bounds[:, 1] - bounds[:, 0]",
        "gpsn": "6",
        "priorsnscale": "0.1",
        "priorsnmin": "sn",
        "priorsfmu": "np.log(sf)",
        "priorsfsigma": "1.",
        "priorsfmin": "1e-6",
        "priorella": "ell / 100",
        "priorellb": "ell * 2",
        "priormumu": "mu",
        "priormuvar": "sf",
        "mcmcburn": 100,
        "mcmcn": 10,
        "eixi": 0.0,
        "pixi": 0.05,
        "ucbdelta": 0.1,
        "ucbxi": 0.2,
        "thompsonn": 100,
        "thompsonrng": 0
    }

    with open(file, "w") as f:
        for (p, v) in param.items():
            if defaultparams.has_key(p):
                if v == defaultparams[p]:
                    continue
                try:
                    if float(v) == defaultparams[p]:
                        continue
                except:
                    pass
                try:
                    if int(v) == defaultparams[p]:
                        continue
                except:
                    pass
            if p == "outputdir":
                continue
            elif p == "bounds":
                if v is not None:
                    for b in v:
                        f.write(str(p) + "," + ",".join(map(str, b)) + "\n")
            elif type(v) in (str, int, float, unicode, bool):
                if defaultparams.has_key(p):
                    if type(defaultparams[p]) == bool:
                        f.write(str(p) + "," + str(bool(v)) + "\n")
                    else:
                        f.write(str(p) + "," + str(v) + "\n")
                else:
                    f.write(str(p) + "," + str(v) + "\n")
            else:
                f.write(str(p) + "," + ",".join(v) + "\n")

    if console is not None:
        console.log("Succesfully exported settingts to >" + str(file))
