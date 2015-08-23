try:
    from Tkinter import Frame, Toplevel, Message, CENTER, LEFT, BOTH, RIGHT, Label, W, E, S, N, Tk, NW, StringVar, \
        OptionMenu, DISABLED, NORMAL, FLAT
except:
    from tkinter import Frame, Toplevel, Message, CENTER, LEFT, BOTH, RIGHT, Label, W, E, S, N, Tk, NW, StringVar, \
        OptionMenu, DISABLED, NORMAL, FLAT

import Tkinter as Tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as pl

from factories import header, headersmall, infoh, infov
from styles import Styles


# The Observation stage panel
class observation():
    # Set up all the data fields and frames
    def __init__(self, contentframe, console, params):
        self.frame = contentframe
        self.iniparams = {
            "totbest": "-",
            "x": [],
            "y": [],
            "mu": [],
            "var": [],
            "time": []
        }
        self.lockgraph = False
        self.console = console
        self.params = params
        self.experimentdata()
        self.startgraph()

    # Destroy the Frame
    def destroy(self):
        self.frame.destroy()

    # Create the widgets
    def experimentdata(self):
        f = Frame(self.frame)
        self.experimentframe = f
        f.config(padx=20, pady=20, bg=Styles.colours["grey"])
        modeldetails = header(f, "Model:")
        fm = Frame(f)
        fm.config(padx=20, pady=20, bg=Styles.colours["grey"])
        infoh(fm, "Command:", self.params["command"].get(), 0, 0)
        infoh(fm, "Model Input:", self.params["modelinput"].get(), 1, 0)
        infoh(fm, "Model Output:", self.params["modeloutput"].get(), 2, 0)

        self.numexperitments = header(f, "Current Experiment: 0/0")
        _, self.iterinfo = infov(f, "Iteration:", "-", 5, 0)
        _, self.kernelinfo = infov(f, "Kernel:", "-", 5, 1)
        _, self.policyinfo = infov(f, "Policy:", "-", 5, 2)

        resultsframe = Frame(f)
        resultsframe.config(bg=Styles.colours["grey"])
        headersmall(resultsframe, "Best Result:       ").grid(row=0, column=0, sticky=W + E + N + S)

        Label(resultsframe, text="Current:", font=Styles.fonts["entry"], bg=Styles.colours["grey"], width=9).grid(row=0,
                                                                                                                  column=1,
                                                                                                                  sticky=E)
        self.curbestlabel = Label(resultsframe, bg=Styles.colours["grey"], text="-", width=20, font=Styles.fonts["h2"])
        self.curbestlabel.grid(row=0, column=2, sticky=W)

        Label(resultsframe, text="Overall:", font=Styles.fonts["entry"], bg=Styles.colours["grey"], width=9).grid(row=1,
                                                                                                                  column=1,
                                                                                                                  sticky=E)
        self.totbestlabel = Label(resultsframe, text=self.iniparams["totbest"], bg=Styles.colours["grey"], width=20,
                                  font=Styles.fonts["h2"])
        self.totbestlabel.grid(row=1, column=2, sticky=W)

        curresultsframe = Frame(f)
        curresultsframe.config(bg=Styles.colours["grey"])

        headersmall(curresultsframe, "Latest Iteration: ").grid(row=0, column=0, sticky=W + E + N + S)

        Label(curresultsframe, text="y:", font=Styles.fonts["entry"], bg=Styles.colours["grey"], width=9).grid(row=0,
                                                                                                               column=1,
                                                                                                               sticky=E)
        self.cury = Label(curresultsframe, text="-", width=20, font=Styles.fonts["h2"], bg=Styles.colours["grey"])
        self.cury.grid(row=0, column=2, sticky=W)

        Label(curresultsframe, text="mu:", font=Styles.fonts["entry"], bg=Styles.colours["grey"], width=9).grid(row=1,
                                                                                                                column=1,
                                                                                                                sticky=E)
        self.curmu = Label(curresultsframe, text=self.iniparams["totbest"], bg=Styles.colours["grey"], width=20,
                           font=Styles.fonts["h2"])
        self.curmu.grid(row=1, column=2, sticky=W)

        Label(curresultsframe, text="var:", font=Styles.fonts["entry"], bg=Styles.colours["grey"], width=9).grid(row=2,
                                                                                                                 column=1,
                                                                                                                 sticky=E)
        self.curvar = Label(curresultsframe, text=self.iniparams["totbest"], bg=Styles.colours["grey"], width=20,
                            font=Styles.fonts["h2"])
        self.curvar.grid(row=2, column=2, sticky=W)

        modeldetails.grid(row=0, column=0, columnspan=3, sticky=W + E + N + S)

        fm.grid(row=1, column=0, columnspan=3, sticky=W + E + N + S, padx=20)

        self.numexperitments.grid(row=4, column=0, columnspan=3, sticky=W + E + N + S)

        resultsframe.grid(row=7, column=0, columnspan=3, sticky=W + E + N + S)
        curresultsframe.grid(row=8, column=0, columnspan=3, sticky=W + E + N + S)
        f.grid(row=0, column=1, sticky=W + E + N + S)

    # Create the graph base
    def startgraph(self):
        pl.style.use('ggplot')
        root = Frame(self.frame)
        self.graphframem = root
        root.config(padx=20, pady=20, bg=Styles.colours["grey"])
        self.graphtype = StringVar(root)
        self.graphtype.set("Graph: Running Best (Overview)")  # initial value
        self.option = OptionMenu(root, self.graphtype, "Graph: Objective Value", "Graph: Running Best (Zoom)",
                                 "Graph: Running Best (Overview)", "Graph: Variance", "Graph: Variance (Last 25)",
                                 "Graph: Objective Value (Last 25)", "Graph: Running Best (Last 25)",
                                 "Graph: Time (seconds)")
        self.option.config(padx=5, pady=5, justify=LEFT, font=Styles.fonts["h1"], relief=FLAT,
                           highlightbackground=Styles.colours["yellow"], highlightthickness=1,
                           bg=Styles.colours["grey"])
        self.option.pack(fill=BOTH)

        def callback(*args):
            if not self.lockgraph:
                self.updategraph()

        self.graphtype.trace("w", callback)

        self.graphfigure = Figure(figsize=(6, 6), dpi=70, facecolor=Styles.colours["grey"])
        self.graphframe = self.graphfigure.add_subplot(111, axisbg=Styles.colours["darkGrey"])

        self.graphframe.set_xlabel('Iteration')
        self.graphframe.set_ylabel('Objective Value')
        canvas = FigureCanvasTkAgg(self.graphfigure, master=root)

        canvas.show()
        canvas.get_tk_widget().configure(background=Styles.colours["grey"], highlightcolor=Styles.colours["grey"],
                                         highlightbackground=Styles.colours["grey"])
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        root.grid(row=0, column=0)
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)

    # Update a variable on the page
    def updatevar(self, var, value):

        if var == "kernel":
            self.kernelinfo.config(text=value.upper())
            self.lockvar = True
            self.iniparams.update({
                "x": [],
                "y": [],
                "mu": [],
                "var": [],
                "time": []
            })
            self.lockvar = False
        if var == "policy":
            self.policyinfo.config(text=value.upper())
            self.lockvar = True
            self.iniparams.update({
                "x": [],
                "y": [],
                "mu": [],
                "var": [],
                "time": []
            })
            self.lockvar = False
        if var == "expnum":
            self.numexperitments.config(text="Current Experiment:" + value)
        if var == "data":
            self.lockvar = True
            for k, v in value.items():
                self.iniparams[k] += [v]
            self.lockvar = False
            if not self.lockgraph:
                self.updategraph()
        if var == "inidata":
            self.lockvar = True
            for k, v in value.items():
                self.iniparams[k] += v
            self.lockvar = False

    # Update the graph
    def updategraph(self):
        if not self.lockvar:
            self.lockgraph = True
            self.option.config(state=DISABLED)
            self.graphframe.clear()
            y = self.iniparams["y"]
            ymax = np.max(y)
            ylen = len(y)

            def updatefields():
                self.curbestlabel.config(text=str(ymax))
                self.iterinfo.config(text=str(ylen))
                self.curmu.config(text=str(self.iniparams["mu"][-1]))
                self.curvar.config(text=str(self.iniparams["var"][-1]))
                self.cury.config(text=str(y[-1]))
                if self.iniparams["totbest"] is "-" or ymax > self.iniparams["totbest"]:
                    self.totbestlabel.config(text=str(ymax))

            def addlabels():
                self.graphframe.set_xlabel('Iteration')
                self.graphframe.set_ylabel('Objective Value')

            def bestrungraphz():
                self.graphframe.plot([yi if yi > np.max(y[:i + 1]) else np.max(y[:i + 1]) for i, yi in enumerate(y)],
                                     'b', linewidth=3)  # plot performance
                self.graphframe.axis((0, ylen, ymax * 1.5, ymax * 1.5 if ymax > 0 else ymax * 0.5))
                addlabels()

            def bestrungrapho(n):
                bestrun = [yi if yi > np.max(self.iniparams["y"][:i + 1]) else np.max(y[:i + 1]) for i, yi in
                           enumerate(self.iniparams["y"])]
                self.graphframe.plot(bestrun[-n:] if ylen >= n else bestrun, 'y', linewidth=3)  # plot performance
                self.graphframe.axis("auto")
                addlabels()

            def objectivevaluegraph(n):
                self.graphframe.plot(y[-n:] if ylen >= n else y, 'r', linewidth=3)  # plot performance
                self.graphframe.axis("auto")
                addlabels()

            def vargraph(n):
                self.graphframe.plot(
                    self.iniparams["var"][-n:] if len(self.iniparams["var"]) >= n else self.iniparams["var"], 'm',
                    linewidth=3)  # plot performance
                self.graphframe.axis("auto")
                addlabels()

            def timegraph():
                self.graphframe.plot(self.iniparams["time"], 'c', linewidth=3)  # plot performance
                self.graphframe.axis("auto")
                self.graphframe.set_xlabel('Iteration')
                self.graphframe.set_ylabel('Time in Seconds')

            graphfunc = {
                "Graph: Objective Value": lambda: objectivevaluegraph(0),
                "Graph: Running Best (Zoom)": bestrungraphz,
                "Graph: Running Best (Overview)": lambda: bestrungrapho(0),
                "Graph: Variance": lambda: vargraph(0),
                "Graph: Objective Value (Last 25)": lambda: objectivevaluegraph(25),
                "Graph: Running Best (Last 25)": lambda: bestrungrapho(25),
                "Graph: Variance (Last 25)": lambda: vargraph(25),
                "Graph: Time (seconds)": timegraph
            }
            updatefields()
            graphfunc[self.graphtype.get()]()
            self.graphfigure.canvas.draw()
            self.option.config(state=NORMAL)
            self.lockgraph = False
