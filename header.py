__author__ = 'doniy'

from Tkinter import Frame,RIGHT,CENTER,W,E,S,N,BOTH,LEFT,Message
from styles import Styles
from fileparser import *
import tkFileDialog
from factories import camobutton,qbutton,yellowbutton
from selection import AdvancedSettings

class mainheader():
    def __init__(self, master, console,params):
        self.frame = Frame(master)
        self.frame.config(padx=5, pady=5, bg=Styles.colours["darkGrey"])
        self.frame.grid(row=0, column=0, sticky=W + E + N + S,columnspan=2)
        self.title = Message(self.frame, text="ProjectB: Selection",
                        justify=CENTER, bg=Styles.colours["darkGrey"],
                        foreground=Styles.colours["yellow"],
                        width=300, font=Styles.fonts["h1"])

        def importsettings(event):
            f = tkFileDialog.askopenfilename(parent=master, title='Choose a file')
            parsemodifycustomvar(params,parsein(f,parseintosimple(params),console))
            console.ready("model")
            console.ready("bayes")

        def exportfile(event):
            f = tkFileDialog.asksaveasfilename(parent=master, title='Choose a file')
            parseout(f,parseintosimple(params),console)

        self.bimport = camobutton(self.frame, "Import Settings", 15,importsettings)
        self.bexport = camobutton(self.frame, "Export Settings", 15,exportfile)
        self.badvset = yellowbutton(self.frame, "Advanced Settings", 20)

        self.badvset.bind("<Button-1>", lambda a: AdvancedSettings(console,params))
        self.qb = qbutton(self.frame)

        self.title.pack(side=LEFT, fill=BOTH, padx=5, pady=5)
        self.qb.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        self.badvset.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        self.bexport.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)
        self.bimport.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)

    def destroy(self):
        self.frame.destroy()

    def observationstage(self):
        self.bimport.destroy()
        self.bexport.destroy()
        self.badvset.destroy()
        self.title.config(text="ProjectB: Observation")

    def evaluationstage(self):
        self.title.config(text="ProjectB: Evaluation")