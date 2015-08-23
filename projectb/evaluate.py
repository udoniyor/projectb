from Tkinter import Frame, Toplevel, Message,CENTER,LEFT,BOTH,RIGHT,Label,W,E,S,N,Tk,NW,StringVar,OptionMenu,DISABLED,NORMAL,FLAT,TOP,END
import tkFileDialog
from factories import customvar,camobutton,qbutton,header,headersmall,infoh,infov,yellowbutton,deactivatebutton
from styles import Styles


import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.lines as mlines
import matplotlib

import matplotlib.pyplot as pl
import Tkinter as Tk
import decimal
# matplotlib.use('TkAgg')
import sys

#The Evaluation stage panel
class evaluation():

    #Creates all the frames and inserts the widgets
    def __init__(self, params, experiments,connector,master,console):
        self.frame = Frame(master)
        self.frame.config(padx=20,pady=20,bg=Styles.colours["grey"])
        self.footer = Frame(master)
        self.footer.config(padx=5,pady=5,bg=Styles.colours["darkGrey"])
        self.experiments = experiments
        self.params = params
        self.connector = connector
        self.evaluationUI()
        self.frame.grid(row=1, column=0,columnspan=1, sticky=W + E + N + S)
        self.console = console
        self.master = master

    #The content widget
    def evaluationUI(self):
        modeldetails = header(self.frame,"Model")
        fm = Frame(self.frame)
        fm.config(bg=Styles.colours["grey"])
        resultdetails = header(self.frame,"Results")
        resultsframe = Frame(self.frame)
        resultsframe.config(bg=Styles.colours["grey"])


        #Model details
        Message(fm, text="Command:", font=Styles.fonts["h2"], bg=Styles.colours["grey"],width=200).grid(row=0,column=0,sticky=E)
        Message(fm, text=self.params["command"].get(), font=Styles.fonts["h3"], bg=Styles.colours["grey"],width=415).grid(row=0,column=1,sticky=W)
        Message(fm, text="Model Input:", font=Styles.fonts["h2"], bg=Styles.colours["grey"],width=200).grid(row=1,column=0,sticky=E)
        Message(fm, text=self.params["modelinput"].get(), font=Styles.fonts["h3"], bg=Styles.colours["grey"],width=415).grid(row=1,column=1,sticky=W)
        Message(fm, text="Model Output:", font=Styles.fonts["h2"], bg=Styles.colours["grey"],width=200).grid(row=2,column=0,sticky=E)
        Message(fm, text=self.params["modeloutput"].get(), font=Styles.fonts["h3"], bg=Styles.colours["grey"],width=415).grid(row=2,column=1,sticky=W)

        #Table Headers
        Label(resultsframe,text=" # ", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=5).grid(row=0,column=0,sticky=E)
        Label(resultsframe,text="Kernel:", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=9).grid(row=0,column=1,sticky=E)
        Label(resultsframe,text="Policy:", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=9).grid(row=0,column=2,sticky=E)
        Label(resultsframe,text="Iterations:", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=14).grid(row=0,column=3,sticky=E)
        Label(resultsframe,text="Best Result:", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=14).grid(row=0,column=4,sticky=E)
        Label(resultsframe,text="Time (s):", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=14).grid(row=0,column=5,sticky=E)
        Label(resultsframe,text="", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=14).grid(row=0,column=6,sticky=E)

        #Table Data
        for i,e in enumerate(self.experiments):
            if e.has_key("iterfinish"):
                Label(resultsframe,text=str(i+1), font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=5).grid(row=i+1,column=0,sticky=E)
                Label(resultsframe,text=e["kernel"].upper(), font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=9).grid(row=i+1,column=1,sticky=E)
                Label(resultsframe,text=e["policy"][0].upper(), font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=9).grid(row=i+1,column=2,sticky=E)
                Label(resultsframe,text=e["iterfinish"], font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=14).grid(row=i+1,column=3,sticky=E)
                Label(resultsframe,text="{0:.5f}".format(e["best"]), font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=14).grid(row=i+1,column=4,sticky=E)
                Label(resultsframe,text="{0:.2f}".format(e["time"]), font=Styles.fonts["entryFilled"],bg=Styles.colours["grey"],width=14).grid(row=i+1,column=5,sticky=E)
                yellowbutton(resultsframe,"Query",10,lambda x: self.query(e["modelid"])).grid(row=i+1,column=6,sticky=E,pady=3)
            else:
                Label(resultsframe,text=str(i+1), font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=5).grid(row=i+1,column=0,sticky=E)
                Label(resultsframe,text=e["kernel"].upper(), font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=9).grid(row=i+1,column=1,sticky=E)
                Label(resultsframe,text=e["policy"][0].upper(), font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=9).grid(row=i+1,column=2,sticky=E)
                Label(resultsframe,text="Not Started", font=Styles.fonts["entry"],bg=Styles.colours["grey"],width=14).grid(row=i+1,column=3,sticky=W+E,columnspan=3)

        #Footer buttons
        y1 = camobutton(self.footer,"Save Console Logs",18,click=lambda x: self.saveconsole())
        y1.config(font=Styles.fonts["h2"])
        y1.pack(side=LEFT,fill=BOTH, padx=5, pady=5)

        y2 = camobutton(self.footer,"Output Directory",18,lambda x: self.opendir())
        y2.config(font=Styles.fonts["h2"])
        y2.pack(side=LEFT,fill=BOTH, padx=5, pady=5)

        y3 = yellowbutton(self.footer,"Exit",18,lambda x: self.closeall())
        y3.config(font=Styles.fonts["h2"])
        y3.pack(side=RIGHT,fill=BOTH, padx=5, pady=5)


        #Grid everything
        #Model Title and Frame
        modeldetails.grid(row=0,column=0,columnspan=3,sticky=W + E + N + S)
        fm.grid(row=1, column=0,columnspan=3,sticky=W + E + N + S)
        #Result Title and Frame
        resultdetails.grid(row=2, column=0,columnspan=3,sticky=W + E + N + S)
        resultsframe.grid(row=3, column=0,columnspan=3,sticky=W + E + N + S)
        #Footer
        self.footer.grid(row=3,column=0,sticky=W+E+N+S,columnspan=2)

    #Close the connector and then the main window
    def closeall(self):
        self.connector.closestage()
        self.master.destroy()

    #Query the bayes opt process for the posterior data
    def query(self,id):
        f =tkFileDialog.askopenfilename(parent=self.master, title='Choose query file')
        self.connector.queryposterior(f,id)

    #Save the data from the Console
    def saveconsole(self):
        f = tkFileDialog.asksaveasfilename(parent=self.master,initialfile="log.txt", title='Choose where to save log file')
        try:
            file = open(f, "a+")
            for line in self.console.getconsolefield().get(1.0, END):
                file.write(line)
            file.close()
            self.console.log("Succesfully exported logs")
        except:
            self.console.log("Something went wrong with exporting logs, try a different location")

    #Open the output directory
    def opendir(self):
        import platform
        import os
        import subprocess
        dir = self.params["outputdir"].get()
        platform = platform.system().lower()
        if platform == "windows":os.startfile("." if dir == "Output Directory" else dir)
        if platform == "darwin":subprocess.call(['/usr/bin/open', "~" if dir == "Output Directory" else dir])
        if platform == "linux":subprocess.call(['xdg-open', "." if dir == "Output Directory" else dir])




