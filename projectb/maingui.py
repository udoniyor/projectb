try:
    from Tkinter import Tk, FALSE, Frame, BOTH, END, DISABLED, Message, LEFT, RIGHT, NORMAL, CENTER, Text, Scrollbar, \
        FLAT, N, S, E, W
except:
    from tkinter import Tk, FALSE, Frame, BOTH, END, DISABLED, Message, LEFT, RIGHT, NORMAL, CENTER, Text, Scrollbar, \
        FLAT, N, S, E, W

from multiprocessing import Process, Pipe, freeze_support
import threading

from selection import ModelFrame, ModelBayes
from styles import Styles
from factories import yellowbutton, deactivatebutton, activateyellowbutton, customvar, redbutton
from observation import observation
from evaluate import evaluation
from fileparser import parsemodifycustomvar, parsein, parseintosimple
import bayesianthread
from header import mainheader
from consoles import console


# Main GUI window class
class projectbgui:
    def __init__(self, paramin=None, paramout=None):
        self.master = Tk()
        self.master.title("ProjectB")
        self.master.resizable(width=FALSE, height=FALSE)
        self.console = console()
        # Set up intial parameters
        try:
            import nlopt
            solver = "direct"
        except:
            solver = "lbfgs"
        self.params = {
            "command": customvar(" i.e. python C://Users/Desktop/model/final4.py", "Model Command", self.console),
            "modelinput": customvar("Select Input File", "Model Input File", self.console),
            "modeloutput": customvar("Select Output File", "Model Output File", self.console),
            "bounds": [],
            "outputdir": customvar("Output Directory", "Output file location", self.console),
            "policies": [customvar(True, "EI", self.console), customvar(False, "PI", self.console),
                         customvar(False, "UCB", self.console), customvar(False, "Thompson", self.console)],
            "kernels": [customvar(True, "SE", self.console), customvar(False, "Matern 5", self.console),
                        customvar(False, "Matern 3", self.console), customvar(False, "Matern 1", self.console)],
            "iter": customvar(150, "Iterations", self.console),
            "objective": customvar("max", "Objective", self.console),
            "solver": customvar(solver, "Solver", self.console),
            "initializer": customvar("sobol", "Initialization", self.console),
            "initializernum": customvar(30, "Samples to sample by the initializer", self.console),
            "recommender": customvar("latent", "Recommender", self.console),
            "normalize": customvar(False, "Normalize", self.console),
            "data": customvar("Select Data File", "Data File URI", self.console),
            "dims": customvar(2, "Dimension Scheduler dimensions per iterations", self.console),
            "dimscheudler": customvar(False, "Dimension Scheduler", self.console),
            "gpsf": customvar("np.std(Y)", "GP sf", self.console),
            "gpmu": customvar("np.mean(Y)", "GP mu", self.console),
            "gpell": customvar("bounds[:, 1] - bounds[:, 0]", "GP ell", self.console),
            "gpsn": customvar("6", "GP sn", self.console),
            "priorsnscale": customvar("0.1", "Horseshoe Prior sn scale", self.console),
            "priorsnmin": customvar("sn", "Horseshoe Prior sn min", self.console),
            "priorsfmu": customvar("np.log(sf)", "Log Normal Prior sf mu", self.console),
            "priorsfsigma": customvar("1.", "Log Normal Prior sf sigma", self.console),
            "priorsfmin": customvar("1e-6", "Log Normal Prior sf min", self.console),
            "priorella": customvar("ell / 100", "Uniform Prior ell a", self.console),
            "priorellb": customvar("ell * 2", "Uniform Prior ell b", self.console),
            "priormumu": customvar("mu", "Gaussian Prior mu", self.console),
            "priormuvar": customvar("sf", "Gaussian Prior var", self.console),
            "mcmcburn": customvar(100, "MCMC Burn", self.console),
            "mcmcn": customvar(10, "MCMC number of models", self.console),
            "eixi": customvar(0.0, "EI policy ei", self.console),
            "pixi": customvar(0.05, "PI policy xi", self.console),
            "ucbdelta": customvar(0.1, "UCB policy delta", self.console),
            "ucbxi": customvar(0.2, "UCB policy xi", self.console),
            "thompsonn": customvar(100, "Thompson policy Iterations", self.console),
            "thompsonrng": customvar(0, "Thompson policy RNG", self.console)
        }


        self.isready = {"model": False, "bayes": True}
        self.headerframe = mainheader(self.master, self.console, self.params,self)
        self.currentstage = self.selectionstage()
        self.footerframe = self.concolefooter()

        # Process if intial parameters were given
        if paramin is not None:
            parsemodifycustomvar(self.params, parsein(paramin, parseintosimple(self.params), self.console))
            self.ready("model")

        self.master.mainloop()

    # Create the Selection stage panels
    def selectionstage(self):
        contentframe = Frame(self.master)
        ModelFrame(contentframe, self.console, self.params, 0, 0, self)
        ModelBayes(contentframe, self.console, self.params, 0, 1, self)
        contentframe.grid(row=1, column=0)
        return contentframe

    # Create the console footer widgets
    def concolefooter(self):
        footerframe = Frame(self.master)
        footerframe.config(padx=5, pady=5, bg=Styles.colours["darkGrey"])
        title = Message(footerframe, text="Console:",
                        justify=CENTER, bg=Styles.colours["darkGrey"],
                        foreground=Styles.colours["yellow"],
                        width=100, font=Styles.fonts["entry"])

        consoletext = Text(footerframe, height=5, width=80, bg=Styles.colours["darkGrey"],
                           foreground=Styles.colours["grey"], state=NORMAL, relief=FLAT, font=Styles.fonts["console"])
        consoletext.insert(END, "Welcome to Project Bi")
        consoletext.config(state=DISABLED)
        self.console.setconsolefield(consoletext)
        scroll = Scrollbar(footerframe, command=consoletext.yview, relief=FLAT)
        consoletext.configure(yscrollcommand=scroll.set)

        self.boptimize = yellowbutton(footerframe, "Optimize", 20, lambda e: self.observerstage())
        deactivatebutton(self.boptimize)
        self.boptimize.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        self.boptimize.configure(font=Styles.fonts["h1Button"])

        title.pack(side=LEFT, fill=BOTH)
        scroll.pack(side=LEFT, fill=BOTH)
        consoletext.pack(side=LEFT, fill=BOTH)
        footerframe.grid(row=2, column=0, sticky=W + E + N + S, columnspan=2)

        return footerframe

    # Update the ready parameter for the given section
    def ready(self, section):
        self.isready[section] = True
        if False not in self.isready.values():
            activateyellowbutton(self.boptimize, lambda e: self.observerstage())

    # Update the ready parameter for the given section
    def notready(self, section):
        deactivatebutton(self.boptimize)
        self.isready[section] = False

    # Destroy current stage and
    # Create the Observation stage panels
    def observerstage(self):
        self.currentstage.destroy()
        self.headerframe.observationstage()
        contentframe = Frame(self.master)
        self.currentstage = observation(contentframe, self.console, self.params)
        contentframe.grid(row=1, column=0)
        self.connector = guiconnector(self.console, self.currentstage, self.modelsready)
        self.connector.start(self.params)
        redbutton(self.boptimize, "End")

        def closeWindow():
            self.connector.closestage()
            self.master.destroy()

        def endbayes(e):
            self.boptimize.config(text="Saving Data...")
            self.connector.endbayesopt()

        self.master.protocol("WM_DELETE_WINDOW", closeWindow)
        self.boptimize.bind("<Button-1>", endbayes)

    # Update the button once bayes opt has finished
    def modelsready(self, experiments):
        self.boptimize.config(text="Models")
        activateyellowbutton(self.boptimize, lambda e: self.evaluationstage(experiments))

    # Destroy current stage and
    # Create the Evaluation stage panels
    def evaluationstage(self, experiments):
        self.currentstage.destroy()
        self.boptimize.destroy()
        self.headerframe.evaluationstage()
        evaluation(self.params, experiments, self.connector, self.master, self.console)


"""
Following class provides a link between the UI and the BayesOpt process via pipes.
"""


class guiconnector():
    def __init__(self, console, observer, modelsready):
        self.console = console
        self.observer = observer
        self.modelsready = modelsready

    # Starts up data structures
    def start(self, params):
        self.a, self.b = Pipe(duplex=True)
        freeze_support()
        if __name__ == "maingui":
            self.p = Process(target=bayesianthread.BayesianOptProcess, kwargs={
                "params": parseintosimple(params),
                "pipein": self.a,
                "pipeout": self.b
            })
            self.t = threading.Thread(target=self.bayesoptlistener)
            self.t.start()
            self.p.start()

    # Listnere for data from the BayesOpt Process
    def bayesoptlistener(self):
        pipein = self.a
        pipeout = self.b
        stop = False;
        while not stop:
            if pipein.poll():
                output = pipein.recv()
                if output.has_key("stop_connector"):
                    break
                if output.has_key("stopped_bayes"):
                    self.modelsready(output["stopped_bayes"])
                for k, v in output.items():
                    if k == "console":
                        self.console.log(v["text"],v["verbose"])
                    else:
                        self.observer.updatevar(k, v)

    # Request the BayesOpt Process for the posterior of the given model
    def queryposterior(self, xdata, modelid):
        self.a.send({"posterior": xdata, "modelid": modelid})

    # Finish BayesOpt
    def endbayesopt(self):
        self.a.send({"stop": True, "stop_posterior_connector": True})
        self.console.log("Attempting to stop the Bayesian Optimization")
        self.console.log("Please Wait...")
        self.console.log("Saving the data...")

    # Clear up the processes and close the pipes
    def closestage(self):
        self.b.send({"stop_connector": True})
        self.endbayesopt()
        self.a.close()
        self.b.close()
        self.p.terminate()
