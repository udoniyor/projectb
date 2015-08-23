__author__ = 'doniy'
from Tkinter import NORMAL, END, DISABLED


# A simple console class with verbosity level to filter out messages
class console():
    def __init__(self, textfield=None, verbosity=2):
        self.consolefield = textfield
        self.verbosity = verbosity

    # Check if the verbosity level of the message suits the user and then print
    def __call__(self, message, messageverbosity=2):
        if self.verbosity >= messageverbosity:
            if self.consolefield is not None:
                self.consolefield.config(state=NORMAL)
                self.consolefield.insert(END, "\n >: " + message)
                self.consolefield.yview(END)
                self.consolefield.config(state=DISABLED)
            else:
                print(message)

    def log(self, text):
        self.__call__(text)

    # If used by the GUI, set the textbox to log the text to
    def setconsolefield(self, consolefield):
        self.consolefield = consolefield

    # Get the console field
    def getconsolefield(self):
        return self.consolefield
