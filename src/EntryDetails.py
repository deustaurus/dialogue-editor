from tkinter import *
from tkinter import ttk

class EntryDetails:
    def __init__(self, master, content):
        self.content = content

        frame = Frame(master, width=240, relief=GROOVE, borderwidth=1, padx=2, pady=2)
        frame.grid_propagate(False)
        frame.grid(row=0, column=2, sticky=NSEW, padx=2, pady=2)
        frame.columnconfigure(0, weight=1)

        labels = Frame(frame)
        labels.grid(row=0, column=0, sticky=NSEW)
        
        self.labeltitle = Label(labels, text='', wraplength=230, justify=LEFT)
        self.labeltitle.grid(row=0, column=0, sticky=W)

        sep = ttk.Separator(frame)
        sep.grid(row=1, column=0, sticky=EW)

        buttons = Frame(frame)
        buttons.grid(row=2, column=0, sticky=NSEW)
        self.colorbuttons = []
        self._addColorButton(buttons, 0, '#ff0000')
        self._addColorButton(buttons, 1, '#00ff00')

        self.lastentry = None
        self._rebuildPage()
    
    def _addColorButton(self, master, index, color):
        button = Checkbutton(master, bg=color, activebackground=color)
        button.grid(row=index, column=0, sticky=W, padx=3)
        self.colorbuttons.append(button)

    def refreshView(self):
        if self.lastentry != self.content.editEntry:
            self._rebuildPage()
    
    def _rebuildPage(self):
        self.lastentry = self.content.editEntry
        if self.lastentry == None:
            self.labeltitle.config(text='No Entry Selected')
            return
        self.labeltitle.config(text='Entry:\n' + self.lastentry.getPath())