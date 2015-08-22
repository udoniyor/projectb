__author__ = 'doniy'
from Tkinter import NORMAL, END, DISABLED

class console():
    def __init__(self,textfield=None,verbosity=3):
        self.consolefield = textfield
        self.verbosity = verbosity

    def __call__(self, message,messageverbosity=3):
        if self.verbosity >= messageverbosity:
            if self.consolefield is not None:
                self.consolefield.config(state=NORMAL)
                self.consolefield.insert(END,"\n >: " + message)
                self.consolefield.yview(END)
                self.consolefield.config(state=DISABLED)
            else:
                print(message)

    def log(self,text):
        self.__call__(text)

    def setconsolefield(self,consolefield):
        self.consolefield = consolefield

    def getconsolefield(self):
        return self.consolefield