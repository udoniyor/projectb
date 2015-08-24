import sys
import argparse
from maingui import projectbgui
import fileparser
import bayesianthreadcli
from consoles import console


# Main class to invoke GUI or CLI
def main(argv):
    parser = argparse.ArgumentParser("ProjectB is a Bayesian Optimization GUI with commandline support.")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0,
                        help="increase output verbosity, 1 will inform of only about experiment start and finish. 2 will inform of each iteration")
    parser.add_argument("-cli", help="execute the Bayesian Optimization without the GUI",
                        action="store_true")
    parser.add_argument("paramfile", help="The URI of the parameters file", nargs='?')
    parser.add_argument("outputdir", help="The URI of the output direction", nargs='?')
    args = parser.parse_args()


    # Check if the User has the correct libraries
    try:
        import pybo
        import pygp
        import numpy
    except:
        parser.error(
            "You do not have all the necessary libraries installed. ProjectB requires following libraries to work pybo, pygp, numpy. For the Graphical"
            "User Interace you must have Tkinker module and Matplot library. Please refer to the online documentation for more information.")

    if args.cli:
        if args.paramfile is None:
            parser.error("Specify the parameter file when command line interface is used")
        if args.verbosity >= 0:
            print "verbosity turned 0"
        elif args.verbosity >= 1:
            print "verbosity turned 1"
        elif args.verbosity >= 2:
            print "verbosity turned 2"
        console(verbosity=args.verbosity)
        try:
            import nlopt
            solver = "direct"
        except:
            solver = "lbfgs"
        defaultparams = {
            "command": " i.e. python C://Users/Desktop/model/final4.py",
            "modelinput": "Select Input File",
            "modeloutput": "Select Output File",
            "bounds": [],
            "outputdir": "Output Directory" if args.outputdir is None else args.outputdir,
            "policies": ["ei"],
            "kernels": ["se"],
            "iter": 150,
            "objective": "min",
            "solver": solver,
            "initializer": "sobol",
            "initializernum": 30,
            "recommender": "latent",
            "normalize": False,
            "data": "Select Data File",
            "dims": 2,
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
        # Start Bayes Opt
        bayesianthreadcli.BayesianOptProcess(fileparser.parsein(args.paramfile, defaultparams, console),
                                             console=console)
    else:
        # Check if the Graphical libraries are present
        try:
            try:
                import Tkinter
            except:
                import tkinter
            import matplotlib
        except:
            parser.error(
                "For the Graphical User Interace you must have Tkinker module and Matplot library. Please refer to the online documentation for more information.")

        paramfile = args.paramfile
        outputdir = args.outputdir
        print("Launching the Graphical User Interface of ProjectB")
        projectbgui(paramfile, outputdir)


if __name__ == "__main__":
    main(sys.argv[1:])
