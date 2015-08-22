__author__ = 'doniy'

from styles import Styles
from Tkinter import Button, RIGHT, FLAT, DISABLED, Entry, Message, LEFT, StringVar, IntVar, BooleanVar, Toplevel, Text, \
    END, WORD, Frame,BOTH,DoubleVar,E,W,NORMAL
import tkFileDialog
import os


def qbutton(f, l=None):
    def qbuttonin(event):
        event.widget.config(bg=Styles.colours["helpIN"])

    def qbuttonout(event):
        event.widget.config(bg=Styles.colours["helpB"])

    b = Button(f, text="?", justify=RIGHT, relief=FLAT, bg=Styles.colours["helpB"], width=2,
               font=Styles.fonts["button"], foreground=Styles.colours["helpText"])
    b.bind("<Enter>", qbuttonin)
    b.bind("<FocusIn>", qbuttonin)
    b.bind("<Leave>", qbuttonout)
    b.bind("<FocusOut>", qbuttonout)
    if l is not None:
        b.bind("<Button-1>", l)
    return b

def yellowbutton(f, text, width, click=None):
    def yellowbuttonin(event):
        event.widget.config(bg=Styles.colours["yellowHover"])

    def yellowbuttonout(event):
        event.widget.config(bg=Styles.colours["yellow"])

    b = Button(f, text=text, justify=RIGHT, relief=FLAT, bg=Styles.colours["yellow"], width=width,
               font=Styles.fonts["button"])
    b.bind("<Enter>", yellowbuttonin)
    b.bind("<FocusIn>", yellowbuttonin)
    b.bind("<Leave>", yellowbuttonout)
    b.bind("<FocusOut>", yellowbuttonout)
    if click is not None:
        b.bind("<Button-1>", click)
    return b

def activateyellowbutton(b, click=None):
    def yellowbuttonin(event):
        event.widget.config(bg=Styles.colours["yellowHover"], foreground=Styles.colours["darkGrey"])

    def yellowbuttonout(event):
        event.widget.config(bg=Styles.colours["yellow"], foreground=Styles.colours["darkGrey"])

    b.config(state=NORMAL, justify=RIGHT, relief=FLAT, bg=Styles.colours["yellow"],
               font=Styles.fonts["h1Button"], foreground=Styles.colours["darkGrey"])
    b.bind("<Enter>", yellowbuttonin)
    b.bind("<FocusIn>", yellowbuttonin)
    b.bind("<Leave>", yellowbuttonout)
    b.bind("<FocusOut>", yellowbuttonout)
    if click is not None:
        b.bind("<Button-1>", click)
    return b

def camobutton(f, text, width, click=None):
    def camobuttonin(event):
        event.widget.config(bg=Styles.colours["grey"], foreground=Styles.colours["darkGrey"])

    def camobuttonout(event):
        event.widget.config(bg=Styles.colours["darkGrey"], foreground=Styles.colours["grey"])

    b = Button(f, text=text, justify=RIGHT, relief=FLAT, bg=Styles.colours["darkGrey"], width=width,
               font=Styles.fonts["entryFilled"], foreground=Styles.colours["grey"])
    b.bind("<Enter>", camobuttonin)
    b.bind("<FocusIn>", camobuttonin)
    b.bind("<Leave>", camobuttonout)
    b.bind("<FocusOut>", camobuttonout)
    if click is not None:
        b.bind("<Button-1>", click)
    return b


def deactivatebutton(b):
    def dbuttonin(event):
        event.widget.config(bg=Styles.colours["deactivated"])

    def dbuttonout(event):
        event.widget.config(bg=Styles.colours["deactivated"])

    b.config(state=DISABLED, bg=Styles.colours["deactivated"], foreground=Styles.colours["red"])

    b.bind("<Enter>", dbuttonin)
    b.bind("<FocusIn>", dbuttonin)
    b.bind("<Leave>", dbuttonout)
    b.bind("<FocusOut>", dbuttonout)
    b.unbind("<Button-1>")

def redbutton(b,t):
    def dbuttonin(event):
        event.widget.config(bg=Styles.colours["lightRed"], foreground=Styles.colours["grey"])
    def dbuttonout(event):
        event.widget.config(bg=Styles.colours["red"], foreground=Styles.colours["grey"])

    b.config(text=t, bg=Styles.colours["red"], activeforeground=Styles.colours["grey"])

    b.bind("<Enter>", dbuttonin)
    b.bind("<FocusIn>", dbuttonin)
    b.bind("<Leave>", dbuttonout)
    b.bind("<FocusOut>", dbuttonout)

def entry(f, s, width, file=False, fileCheck=False, button=None):
    defaulttext = s.get()

    def openFileDialog(event):
        if fileCheck:
            s.set(tkFileDialog.askopenfilename(parent=f, title='Choose a file'))
            checkFile()
        else:
            s.set(tkFileDialog.asksaveasfilename(parent=f, title='Create file to save data to'))
        button.bind("<Enter>", lambda event: "break")
        button.bind("<FocusIn>", lambda event: "break")
        button.bind("<Leave>", lambda event: "break")
        button.bind("<FocusOut>", lambda event: "break")
        button.flash()

    def clearEntry(event):
        if s.get() == defaulttext:
            s.set("")
            event.widget.config(font=Styles.fonts["entryFilled"], foreground=Styles.colours["black"])

    def checkFile():
        if os.path.isfile(s.get()):
            e.config(font=Styles.fonts["entryFilled"], bg=Styles.colours["lightGreen"])
        else:
            e.config(font=Styles.fonts["entryFilled"], bg=Styles.colours["lightRed"])

    def restoreEntry(event):
        if s.get() == "":
            s.set(defaulttext)
            event.widget.config(font=Styles.fonts["entry"], foreground=Styles.colours["darkGrey"])
        elif file:
            checkFile()

    e = Entry(f, textvariable=s, font=Styles.fonts["entry"], foreground=Styles.colours["darkGrey"], width=width,
              relief=FLAT)
    e.bind("<FocusIn>", clearEntry)
    e.bind("<FocusOut>", restoreEntry)
    e.bind("<Button-1>", clearEntry)
    if button is not None:
        button.bind("<Button-1>", openFileDialog)

    return e


def header(f, text):
    return Message(f, text=text, padx=5, pady=5, justify=LEFT, width=300, font=Styles.fonts["h1"],
                   highlightbackground=Styles.colours["yellow"], highlightthickness=1, bg=Styles.colours["grey"])


def headersmall(f, text):
    return Message(f, text=text, padx=5, pady=5, justify=LEFT, width=300, font=Styles.fonts["h2"],
                   bg=Styles.colours["grey"])

def infoh(f, text,textv,row,col):
     m = Message(f, text=text, font=Styles.fonts["h2"], bg=Styles.colours["grey"],width=200)
     v = Message(f, text=textv, font=Styles.fonts["h3"], bg=Styles.colours["grey"],width=300)
     m.grid(row=row,column=col,sticky=E)
     v.grid(row=row,column=col+1,sticky=W)
     return (m,v)

def infov(f, text,textv,row,col):
     m = Message(f, text=text, font=Styles.fonts["h2"], bg=Styles.colours["grey"],width=200)
     v = Message(f, text=textv, font=Styles.fonts["h3"], bg=Styles.colours["grey"],width=200)
     m.grid(row=row,column=col)
     v.grid(row=row+1,column=col)
     return (m,v)

def popupwindow(title, height, text):
    def f(event):
        def dest(event):
            w.destroy()

        w = Toplevel()
        w.title(title)
        w.config(bg=Styles.colours["grey"], padx=20, pady=20)

        h = header(w, title)
        t = Text(w, width=30, height=height, relief=FLAT, bg=Styles.colours["grey"], wrap=WORD,
                 font=Styles.fonts["entryFilled"])
        t.insert(END, text)
        b = yellowbutton(w, "OK", 20, dest)
        h.grid(row=0, column=0)
        t.grid(row=1, column=0)
        b.grid(row=2, column=0)

    return f


def smallentry(f, v, w,integer=False):
    def isfloat(input):
        try:
            if integer:
                int(input)
            else:
                float(input)
            return True
        except:
            return False

    validate = f.register(isfloat)
    e = Entry(f, textvariable=v, font=Styles.fonts["entryFilled"], width=w,
                 justify=RIGHT, relief=FLAT, validate="all",validatecommand=(validate, '%P'))

    return e
def smallentryframetext(f,r,c,v,w,t,p=0):
    e = smallentry(f,v,w)
    m = Message(f,text=t, bg=Styles.colours["grey"],width=100)
    m.grid(row=r,column=c,padx=p,sticky=W)
    e.grid(row=r,column=c+1,sticky=E)
    return (m,e)

def smallentryframetextv(f,r,c,v,w,t,p=0):
    e = smallentry(f,v,w)
    m = Message(f,text=t, bg=Styles.colours["grey"],width=100)
    m.grid(row=r,column=c,padx=p,sticky=W)
    e.grid(row=r+1,column=c,sticky=W,padx=3)
    return (m,e)



def customvar(value, id, console):
    def callback(*args):
        change = v.get()
        if type(value) is bool:
            change = "True" if change == 1 else "False"
        console.log(id + " variable is set to " + str(change))

    val = value

    v = StringVar()
    if type(value) is int:
        v = DoubleVar()
    if type(value) is bool:
        val = 1 if value else 0
        v = IntVar()
    v.set(val)
    v.trace("w", callback)

    return v
