try:
    from Tkinter import NW, Frame, W, N, S, Checkbutton, Radiobutton, Label, Toplevel, Text, END, Scrollbar, WORD, E, \
        CENTER, BOTH, X
except:
    from tkinter import NW, Frame, W, N, S, Checkbutton, Radiobutton, Label, Toplevel, Text, END, Scrollbar, WORD, E, \
        CENTER, BOTH, X

from factories import *
from numpy import genfromtxt, fromstring, array
from styles import Styles

"""
 The module contains all the widget initialization and event listeners for the buttons.
"""


# Advanced Settings Window panel
class AdvancedSettings():
    def __init__(self, console, params):
        self.console = console
        self.params = params
        self.advsettingslist = ["solver", "initializer", "recommender", "normalize", "data", "dims", "dimscheudler",
                                "gpsf",
                                "gpmu", "gpell", "gpsn", "priorsnscale", "priorsnmin", "priorsfmu", "priorsfsigma",
                                "priorsfmin", "priorella", "priorellb", "priormumu", "priormuvar", "mcmcburn", "mcmcn",
                                "eixi", "pixi", "ucbdelta", "ucbxi", "thompsonn", "thompsonrng"]
        self.paramsdefaults = dict((k, self.params[k].get()) for k in self.advsettingslist)
        self.toplevel = Toplevel()
        self.toplevel.title("Project B: Advanced Settings")
        self.advheader()
        self.frame = Frame(self.toplevel)
        self.frame.config(padx=20, pady=20, bg=Styles.colours["grey"])
        self.frame.pack(fill=BOTH)

        self.solver()
        self.rec()
        self.initial()
        self.initnumber()
        self.mcmc()
        self.policyset()
        self.dimscheduler()
        Label(self.frame, text="     ").grid(row=1, column=3, sticky=W, columnspan=1)
        self.basicgp()
        self.prior()
        self.data()
        self.submitadvancedsettings()

    def advheader(self):
        headerframe = Frame(self.toplevel)
        headerframe.config(bg=Styles.colours["darkGrey"])
        advancedsettingsheader = Message(headerframe, text="Advanced Settings", bg=Styles.colours["darkGrey"],
                                         justify=CENTER, foreground=Styles.colours["yellow"], pady=5,
                                         width=200, font=Styles.fonts["h1"])
        qb = qbutton(headerframe)
        babout = camobutton(headerframe, "About", 10)
        advancedsettingsheader.pack(side=LEFT, fill=BOTH, padx=5, pady=5)

        qb.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        babout.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        headerframe.pack(fill=BOTH, pady=0)

    def solver(self):
        solverheader = headersmall(self.frame, text="Solvers:")
        direct = Radiobutton(self.frame, text="Direct", variable=self.params["solver"], value="direct",
                             bg=Styles.colours["grey"])
        lbfgs = Radiobutton(self.frame, text="LBFGS", variable=self.params["solver"], value="lbfgs",
                            bg=Styles.colours["grey"])
        message = Message(self.frame, text="Enable normalization if you use lbfgs", width=200)
        try:
            import nlopt
        except:
            self.params["solver"].set("lbfgs")
            self.params["normalize"].set(1)
            direct.config(state=DISABLED)
            message.config(text="You do not have nlopt library installed to use the Direct Solver",
                           bg=Styles.colours["lightRed"])

        normalize = Checkbutton(self.frame, text="Normalize Input", variable=self.params["normalize"],
                                bg=Styles.colours["grey"])

        solverheader.grid(row=1, column=0, sticky=W, columnspan=2)
        direct.grid(row=2, column=0, pady=0, sticky=W, padx=10)
        lbfgs.grid(row=3, column=0, pady=0, sticky=W, padx=10)
        message.grid(row=2, column=1, rowspan=1)
        normalize.grid(row=3, column=1)

    def rec(self):
        recheader = headersmall(self.frame, text="Recommender:")

        incumbent = Radiobutton(self.frame, text="Incumbent", variable=self.params["recommender"], value="incumbent",
                                bg=Styles.colours["grey"])
        latent = Radiobutton(self.frame, text="Latent", variable=self.params["recommender"], value="latent",
                             bg=Styles.colours["grey"])
        observed = Radiobutton(self.frame, text="Observed", variable=self.params["recommender"], value="observed",
                               bg=Styles.colours["grey"])

        recheader.grid(row=4, column=0, sticky=W, columnspan=1)
        incumbent.grid(row=5, column=0, pady=0, sticky=W, padx=10)
        latent.grid(row=6, column=0, pady=0, sticky=W, padx=10)
        observed.grid(row=7, column=0, pady=0, sticky=W, padx=10)

    def initial(self):
        iniheader = headersmall(self.frame, text="Initial points sampler:")

        latin = Radiobutton(self.frame, text="Latin", variable=self.params["initializer"], value="latin",
                            bg=Styles.colours["grey"])
        sobol = Radiobutton(self.frame, text="Sobol", variable=self.params["initializer"], value="sobol",
                            bg=Styles.colours["grey"])
        uniform = Radiobutton(self.frame, text="Uniform", variable=self.params["initializer"], value="uniform",
                              bg=Styles.colours["grey"])

        iniheader.grid(row=4, column=1, sticky=W, columnspan=1)
        latin.grid(row=5, column=1, pady=0, sticky=W, padx=10)
        sobol.grid(row=6, column=1, pady=0, sticky=W, padx=10)
        uniform.grid(row=7, column=1, pady=0, sticky=W, padx=10)

    def initnumber(self):
        f = Frame(self.frame)
        minitnumber = Message(f, text="Numbers of samples to sample:", width=300, bg=Styles.colours["grey"])
        einitnumber = smallentry(f, self.params["initializernum"], 10)
        minitnumber.grid(row=0, column=0, sticky=W, columnspan=1)
        einitnumber.grid(row=0, column=1, sticky=W, columnspan=1, padx=10)

        f.grid(row=9, column=0, sticky=W, columnspan=2)

    def mcmc(self):
        mcmcheader = headersmall(self.frame, text="Markov Chain Monte Carlo Settings:")
        mmcmcn = Message(self.frame, text="Number of GP models:", width=200, bg=Styles.colours["grey"])
        emcmcn = smallentry(self.frame, self.params["mcmcn"], 10)
        mmcmcburn = Message(self.frame, text="Burn:", width=200, bg=Styles.colours["grey"])
        emcmcburn = smallentry(self.frame, self.params["mcmcburn"], 10)

        mcmcheader.grid(row=10, column=0, sticky=W, columnspan=2)
        mmcmcn.grid(row=11, column=0, sticky=W, columnspan=1)
        emcmcn.grid(row=12, column=0, sticky=W, columnspan=1, padx=15)
        mmcmcburn.grid(row=11, column=1, sticky=W, columnspan=1)
        emcmcburn.grid(row=12, column=1, sticky=W, columnspan=1)

    def policyset(self):
        mischeader = headersmall(self.frame, text="Policy Parameters")
        fp = Frame(self.frame)
        smallentryframetextv(fp, 0, 0, self.params["eixi"], 10, "EI xi:")
        smallentryframetextv(fp, 2, 0, self.params["pixi"], 10, "PI xi:")
        smallentryframetextv(fp, 0, 1, self.params["ucbdelta"], 10, "UCB delta:")
        smallentryframetextv(fp, 2, 1, self.params["ucbxi"], 10, "UCB xi:")
        smallentryframetextv(fp, 0, 2, self.params["thompsonn"], 10, "Thompson N:")
        smallentryframetextv(fp, 2, 2, self.params["thompsonrng"], 10, "Thompson RNG:")

        mischeader.grid(row=13, column=0, sticky=W, columnspan=2)
        fp.grid(row=14, column=0, rowspan=4, columnspan=2, sticky=W, padx=10)

    def dimscheduler(self):
        mischeader = headersmall(self.frame, text="Dimension Scheduler")
        f = Frame(self.frame)
        f.config(bg=Styles.colours["grey"])
        smallentryframetext(f, 0, 0, self.params["dims"], 7, "Set Size:")
        checkdimschel = Checkbutton(self.frame, text="Enable", variable=self.params["dimscheudler"])

        mischeader.grid(row=18, column=0, sticky=W, columnspan=2)
        checkdimschel.grid(row=19, column=0, sticky=W, columnspan=1, padx=15)
        f.grid(row=19, column=1, sticky=W + E, columnspan=1)

    def basicgp(self):
        gpheader = headersmall(self.frame, text="Basic GP Settings:")
        f = Frame(self.frame)
        f.config(padx=20, bg=Styles.colours["grey"])
        gpsf, _ = smallentryframetext(f, 0, 0, self.params["gpsf"], 20, "sf:")
        gpmu, _ = smallentryframetext(f, 1, 0, self.params["gpmu"], 20, "mu:")
        Label(f, text="     ").grid(row=0, column=2, sticky=W, rowspan=2)
        gpell, _ = smallentryframetext(f, 0, 3, self.params["gpell"], 20, "ell:")
        gpsn, _ = smallentryframetext(f, 1, 3, self.params["gpsn"], 20, "sn:")

        gpheader.grid(row=1, column=4, sticky=W, columnspan=1)
        Message(self.frame, text="You can use numpy and python syntax to set the parameters from the data where"
                                 " X is the initial and random data, and y is the corresponding output",
                width=400, font=Styles.fonts["entry"]).grid(row=2, column=4, columnspan=2, sticky=W)
        f.grid(row=3, column=4, sticky=W, columnspan=2, rowspan=3)

    def prior(self):
        priorheader = headersmall(self.frame, text="Hyperprior Settings:")
        f = Frame(self.frame)
        f.config(padx=20, bg=Styles.colours["grey"])

        Message(f, text="Horseshoe Prior sn:", width=200, bg=Styles.colours["grey"], font=Styles.fonts["entry"]).grid(
            row=0, column=0, columnspan=2, sticky=W)
        epriorsnscale = smallentry(f, self.params["priorsnscale"], 15)
        mpriorsnscale = Message(f, text="scale:", width=30)
        mpriorsnscale.grid(row=1, column=0, columnspan=1, sticky=E)
        epriorsnscale.grid(row=1, column=1, columnspan=1, sticky=W)
        smallentryframetext(f, 1, 2, self.params["priorsnmin"], 15, "min:")

        Message(f, text="Log Normal Prior sf:", width=200, bg=Styles.colours["grey"], font=Styles.fonts["entry"]).grid(
            row=2, column=0, columnspan=2, sticky=W)
        f3 = Frame(f)
        smallentryframetext(f3, 0, 0, self.params["priorsfmu"], 10, "mu:")
        smallentryframetext(f3, 0, 2, self.params["priorsfsigma"], 10, "sigma:")
        smallentryframetext(f3, 0, 4, self.params["priorsfmin"], 10, "min:")
        f3.grid(row=3, column=0, columnspan=4)

        Message(f, text="Uniform Prior ell:", width=200, bg=Styles.colours["grey"], font=Styles.fonts["entry"]).grid(
            row=4, column=0, columnspan=2, sticky=W)
        smallentryframetext(f, 5, 0, self.params["priorella"], 15, "a:")
        smallentryframetext(f, 5, 2, self.params["priorellb"], 15, "b:")

        Message(f, text="Gaussian Prior mu:", width=200, bg=Styles.colours["grey"], font=Styles.fonts["entry"]).grid(
            row=6, column=0, columnspan=2, sticky=W)
        smallentryframetext(f, 7, 0, self.params["priormumu"], 15, "mu:")
        smallentryframetext(f, 7, 2, self.params["priormuvar"], 15, "var:")

        priorheader.grid(row=6, column=4, sticky=W, columnspan=1)
        Message(self.frame, text="You can set following parameters based on the variables defined in the GP section.",
                width=400, font=Styles.fonts["entry"]).grid(row=7, column=4, columnspan=2)
        f.grid(row=8, column=4, sticky=E + W, columnspan=2, rowspan=10)

    def data(self):
        def datafilesector(e):
            f = tkFileDialog.askopenfilename(parent=self.frame, title='Choose data file')
            self.params["data"].set(self.params["data"])

        dataheader = headersmall(self.frame, text="Add Data")

        if type(self.params["data"].get()) == str or self.params["data"] == [[], []]:
            bdata = yellowbutton(self.frame, "Select Data File", 20, click=None)
            edata = entry(self.frame, self.params["data"], 30, file=True, fileCheck=True, button=bdata)

            edata.grid(row=19, column=4, sticky=E, columnspan=1)
            bdata.grid(row=19, column=5, sticky=W, columnspan=1)
        else:
            bdata = yellowbutton(self.frame, "Data has already been selected", 50, click=None)
            deactivatebutton(bdata)
            bdata.config(state=DISABLED, bg=Styles.colours["deactivated"])
            bdata.grid(row=19, column=4, sticky=W, columnspan=2)

        dataheader.grid(row=18, column=3, sticky=W, columnspan=2)

    def submitadvancedsettings(self):
        def destroywindow(event):
            self.toplevel.destroy()

        def canceladvc(event):
            for k, v in self.paramsdefaults.items():
                self.params[k].set(v)
            destroywindow(event)

        def submitadvc(event):
            self.paramsdefaults = dict((k, self.params[k].get()) for k in self.advsettingslist)
            destroywindow(event)

        f = Frame(self.toplevel)
        f.config(padx=15, pady=15, bg=Styles.colours["darkGrey"])
        submitadv = yellowbutton(f, "Submit", 30, submitadvc)
        canceladv = yellowbutton(f, "Cancel", 20, canceladvc)
        submitadv.pack(side=RIGHT)
        canceladv.pack(side=RIGHT, padx=20)
        f.pack(fill=X)


# Model paramters panel
class ModelFrame():
    def __init__(self, master, console, params, row, col, maingui):
        self.frame = Frame(master)
        self.maingui = maingui
        self.frame.config(padx=20, pady=20, bg=Styles.colours["grey"])
        self.frame.grid(row=row, column=col, sticky=NW)
        self.console = console
        self.params = params
        self.modelparamslist = ["command", "modelinput", "modeloutput", "bounds"]
        self.paramsdefaults = dict(
            (k, self.params[k].get if type(self.params[k]) is not list else []) for k in self.modelparamslist)
        self.headermodel()
        self.modelcmd()
        self.modelio()
        self.bounds()

    def destroy(self):
        self.frame.destroy()

    def headermodel(self):
        headermodel = header(self.frame, "Model Parameters")
        headermodel.grid(row=0, column=0, sticky=W, columnspan=2)

    def modelcmd(self):
        cmdheader = headersmall(self.frame, "Commandline command for the model:")
        ecmd = entry(self.frame, self.params["command"], 65, file=False, fileCheck=False, button=None)

        cmdheader.grid(row=1, column=0, sticky=W, columnspan=2)
        ecmd.grid(row=2, column=0, columnspan=3, pady=5, rowspan=2)
        self.isreadyE(ecmd)
        # Seperator
        Label(self.frame, text="").grid(row=4, column=0, sticky=W, columnspan=2)

    def modelio(self):
        ioheader = header(self.frame, "Select your model I/O:")

        biuri = yellowbutton(self.frame, "Select Input File", 20, click=None)
        bouri = yellowbutton(self.frame, "Select Output File", 20, click=None)
        eiuri = entry(self.frame, self.params["modelinput"], 40, file=True, fileCheck=True, button=biuri)
        eouri = entry(self.frame, self.params["modeloutput"], 40, file=True, fileCheck=True, button=bouri)
        self.isreadyB(biuri)
        self.isreadyB(bouri)
        self.isreadyE(eiuri)
        self.isreadyE(eouri)
        ioheader.grid(row=5, column=0, sticky=W, columnspan=2)
        biuri.grid(row=6, column=2, pady=5)
        bouri.grid(row=7, column=2, pady=5)
        eiuri.grid(row=6, column=0, columnspan=2)
        eouri.grid(row=7, column=0, columnspan=2)
        # Seperator
        Label(self.frame, text="").grid(row=8, column=0, sticky=W, columnspan=2)

    def bounds(self):
        def boundsfilepicker(event):
            f = tkFileDialog.askopenfilename(parent=self.frame, title='Choose bounds a file')

            if os.path.isfile(f):
                try:
                    bounds = genfromtxt(f, delimiter=",")
                    if ((bounds.shape[1] == 2 and (bounds[:, 0] < bounds[:, 1]).all())):
                        self.params["bounds"] = bounds
                        self.console.log("Bounds set to a file: " + str(f))
                        self.console.log("You can now view the bounds")
                        bboundsf.bind("<Enter>", lambda event: "break")
                        bboundsf.bind("<FocusIn>", lambda event: "break")
                        bboundsf.bind("<Leave>", lambda event: "break")
                        bboundsf.bind("<FocusOut>", lambda event: "break")
                    else:
                        texterror = "Bounds file has wrong dimensions, please check the file"
                        self.console.log(texterror)
                        popupwindow("Bounds File error", 2, texterror)
                except:
                    texterror = "Bounds file has wrong format, please check the file"
                    self.console.log(texterror)
                    popupwindow("Bounds File error", 2, texterror)
            else:
                texterror = "Bounds file has not been selected, please select the file"
                self.console.log(texterror)
                popupwindow("Bounds File error", 2, texterror)

        def helpbounds(evemt):
            helpboundsw = Toplevel()
            helpboundsw.title("Help: Bounds")
            helpboundsw.config(bg=Styles.colours["grey"], padx=10, pady=10)

            boundswindowheader = header(helpboundsw, "How to set bounds?")
            t = Text(helpboundsw, width=30, height=20, relief=FLAT, bg=Styles.colours["grey"], wrap=WORD,
                     font=Styles.fonts["entryFilled"])
            t.insert(END,
                     " The bounds give the model maximum and minimum for each input parameter value. You can set the bounds from a file in CSV file"
                     "where first column is the minimum and second column is the maximum, or through the window presented prior.")
            boundswindowheader.grid(row=0, column=0)
            t.grid(row=1, column=0)

        def manualbounds(event):
            def checkbounds(event):
                try:
                    b = minmaxT.get(1.0, END)
                    bounds = array([fromstring(x, dtype=float, sep="-") for x in b.replace(" ", "").split()])
                    if (bounds.shape[1] == 2 and (bounds[:, 0] < bounds[:, 1]).all()):
                        minmaxT.config(bg=Styles.colours["lightGreen"])
                        return True
                    else:
                        minmaxT.config(bg=Styles.colours["lightRed"])
                        return False
                except:
                    minmaxT.config(bg=Styles.colours["lightRed"])
                    return False
                return False

            def submite(event):
                submit()

            def submit():
                if checkbounds(""):
                    b = minmaxT.get(1.0, END)
                    bounds = array([fromstring(x, dtype=float, sep="-") for x in b.replace(" ", "").split()])
                    self.params["bounds"][:] = []
                    for bound in bounds:
                        self.params["bounds"].append(bound.tolist())
                    boundswindow.destroy()
                    if self.checkall():
                        self.maingui("model")
                    self.console.log(
                        "Bounds have been successfully set to following dimensions " + str(len(self.params["bounds"])))

                else:
                    popupwindow("You have not set correct bounds", 5,
                                "The bounds you have set do not correspond to the format specified, please review the bounds you have entered.")(
                        "")
                    if self.checkall():
                        self.maingui("model")
                    else:
                        self.console.notready("model")

            def cancel(event):
                self.params["bounds"] = orginalbounds
                boundswindow.destroy()

            boundswindow = Toplevel()
            boundswindow.title("Bounds")
            boundswindow.config(pady=5, padx=5)
            boundswindow.protocol("WM_DELETE_WINDOW", submit)
            orginalbounds = None
            boundswindowheader = header(boundswindow, "Set model bounds:")
            qB = qbutton(boundswindow, l=popupwindow("How to set bounds?", 8,
                                                     " The bounds give the model maximum and minimum for each input parameter value. You can set the bounds from a file in CSV file"
                                                     "where first column is the minimum and second column is the maximum, or through the window presented prior."))

            minmax = headersmall(boundswindow, "Minimum,Maximum")
            tut = Message(boundswindow, width=250,
                          text="For each dimension set the minimum and maximum, seperated by a minus sign. Each dimension split by a newline (enter)")
            f = Frame(boundswindow)

            minmaxT = Text(f, width=20, height=10, relief=FLAT, padx=15, pady=15,
                           font=Styles.fonts["bounds"])
            minmaxT.bind("<KeyRelease>", checkbounds)
            if (self.params["bounds"] is not []):
                orginalbounds = list(self.params["bounds"])
                for b in self.params["bounds"]:
                    minmaxT.insert(END, str(b[0]) + " - " + str(b[1]) + "\n")
                checkbounds("")

            scroll = Scrollbar(f, command=minmaxT.yview, relief=FLAT)
            minmaxT.configure(yscrollcommand=scroll.set)
            minmaxT.grid(row=0, padx=3, column=0)
            scroll.grid(row=0, column=1)

            submitboundsbutton = yellowbutton(boundswindow, "Submit", 20, submite)
            self.isreadyB(submitboundsbutton, 1000)
            cancelboundsbutton = yellowbutton(boundswindow, "Cancel", 20, cancel)

            boundswindowheader.grid(row=0, column=0, sticky=W, columnspan=1)
            qB.grid(row=0, padx=3, column=1, sticky=E)
            tut.grid(row=1, column=0, columnspan=2)
            minmax.grid(row=2, padx=3, column=0)
            f.grid(row=3, column=0, columnspan=2)

            Label(boundswindow, text="").grid(row=4, column=0, sticky=W, columnspan=2)
            submitboundsbutton.grid(row=5, padx=3, column=0, columnspan=1)
            cancelboundsbutton.grid(row=5, padx=3, column=1, columnspan=1)

        boundsheader = header(self.frame, "Set model bounds:")
        bboundsm = yellowbutton(self.frame, "Set or View Bounds", 40, click=manualbounds)
        bboundsf = yellowbutton(self.frame, "From File", 20, click=boundsfilepicker)
        self.isreadyB(bboundsf)

        # Bounds
        boundsheader.grid(row=9, column=0, sticky=W, columnspan=2)
        bboundsm.grid(row=10, column=0, pady=5, padx=3, columnspan=2)
        bboundsf.grid(row=10, column=2, pady=5, padx=3)

    def isreadyB(self, b, t=3000):
        def timedcheck():
            if self.checkall():
                self.maingui("model")
            else:
                self.console.notready("model")

        def check(event):
            b.after(t, timedcheck)

        b.bind("<ButtonRelease-1>", check)

    def isreadyE(self, e):
        def check(event):
            if self.checkall():
                self.maingui.ready("model")
            else:
                self.maingui.notready("model")

        e.bind("<Tab>", check)

    def checkall(self):
        for k, v in self.paramsdefaults.items():
            if k is "bounds":
                if self.params[k] is []:
                    return False
                else:
                    continue
            if self.params[k].get() == v:
                return False
        return True


# Bayesian Optimization Panel
class ModelBayes():
    def __init__(self, master, console, params, row, col, maingui):
        self.frame = Frame(master)
        self.maingui = maingui
        self.frame.config(padx=20, pady=20, bg=Styles.colours["grey"])
        self.frame.grid(row=row, column=col, sticky=NW)
        self.console = console
        self.params = params
        self.headerbayes()
        self.policy()
        self.kernels()
        self.iterations()
        self.minormax()
        self.outputdir()

    def destroy(self):
        self.frame.destroy()

    def headerbayes(self):
        headerbayes = header(self.frame, "Set the Bayesian Optimization Parameters")
        headerbayes.config(width=400)
        headerbayes.grid(row=0, column=0, sticky=W, columnspan=2)

    def policy(self):
        policyheader = headersmall(self.frame, text="Policies:")
        cei = Checkbutton(self.frame, text="Expected Improvement", variable=self.params["policies"][0])
        cpi = Checkbutton(self.frame, text="Probability Improvement", variable=self.params["policies"][1])
        cucb = Checkbutton(self.frame, text="Upper Confidence Bound", variable=self.params["policies"][2])
        ctho = Checkbutton(self.frame, text="Thompson", variable=self.params["policies"][3])

        self.isreadyR(cei)
        self.isreadyR(cpi)
        self.isreadyR(cucb)
        self.isreadyR(ctho)

        policyheader.grid(row=1, column=0, sticky=W, columnspan=1)
        cei.grid(row=2, column=0, pady=0, sticky=W, padx=10, columnspan=1)
        cpi.grid(row=3, column=0, pady=0, sticky=W, padx=10, columnspan=1)
        cucb.grid(row=4, column=0, pady=0, sticky=W, padx=10, columnspan=1)
        ctho.grid(row=5, column=0, pady=0, sticky=W, padx=10, columnspan=1)

    def kernels(self):
        kernelsheader = headersmall(self.frame, text="Kernels:")

        cse = Checkbutton(self.frame, text="Squared Exponential", variable=self.params["kernels"][0])
        cm5 = Checkbutton(self.frame, text="Matern 5", variable=self.params["kernels"][1])
        cm3 = Checkbutton(self.frame, text="Matern 3", variable=self.params["kernels"][2])
        cm1 = Checkbutton(self.frame, text="Matern 1", variable=self.params["kernels"][3])

        self.isreadyR(cse)
        self.isreadyR(cm5)
        self.isreadyR(cm3)
        self.isreadyR(cm1)

        kernelsheader.grid(row=1, column=1, sticky=W, columnspan=2)
        cse.grid(row=2, column=1, pady=0, sticky=W, padx=10, columnspan=1)
        cm5.grid(row=3, column=1, pady=0, sticky=W, padx=10, columnspan=1)
        cm3.grid(row=4, column=1, pady=0, sticky=W, padx=10, columnspan=1)
        cm1.grid(row=5, column=1, pady=0, sticky=W, padx=10, columnspan=1)

        Label(self.frame, text="", font=("Arial", 6)).grid(row=6, column=0, sticky=W, columnspan=2)

    def iterations(self):
        iterheader = headersmall(self.frame, "Iterations:")
        e = smallentry(self.frame, self.params["iter"], 10, True)
        iterheader.grid(row=7, column=0, sticky=W, columnspan=1)
        self.isreadyR(e, "<FocusOut>")
        e.grid(row=8, column=0, sticky=W, padx=25)

    def minormax(self):
        objheader = headersmall(self.frame, text="Objective:")

        rmim = Radiobutton(self.frame, text="Minimize", variable=self.params["objective"], value="min")
        rmax = Radiobutton(self.frame, text="Maximize", variable=self.params["objective"], value="max")

        objheader.grid(row=7, column=1, sticky=W, columnspan=2)
        rmim.grid(row=8, column=1, pady=0, sticky=W, padx=10)
        rmax.grid(row=9, column=1, pady=0, sticky=W, padx=10)

        # Label(self.frame, text="", font=("Arial", 12)).grid(row=10, column=0, sticky=W, columnspan=2)

    def outputdir(self):
        iframe = Frame(self.frame)
        iframe.config(padx=5, pady=5)
        iframe.grid(row=10, column=0, sticky=W + E + N + S, columnspan=3, rowspan=2)
        objheader = headersmall(iframe, text="Model Output Directory (Optional):")
        boutfile = yellowbutton(iframe, "Select Directory", 14, click=None)
        eoutfiledir = entry(iframe, self.params["outputdir"], 32, file=True, fileCheck=False, button=boutfile)
        objheader.grid(row=0, column=0, sticky=W, columnspan=2)
        boutfile.grid(row=1, column=2, pady=5)
        eoutfiledir.grid(row=1, column=0, columnspan=2)

    def isreadyR(self, r, e=None):
        def check():
            if self.checkall():
                self.maingui.ready("bayes")
            else:
                self.maingui.notready("bayes")

        if e is None:
            r.config(command=check)
        else:
            r.bind(e, lambda e: check())

    def checkall(self):
        p = sum([v.get() for v in self.params["policies"]])
        k = sum([v.get() for v in self.params["kernels"]])
        i = self.params["iter"].get()
        return p and k and i
