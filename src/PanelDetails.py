from tkinter import *
from tkinter import ttk
from DialogueData import EntryType, EntryColors
from Content import Content

class PanelDetails:
    def __init__(self, master):
        frame = Frame(master, width=140, padx=2)
        frame.grid_propagate(False)
        frame.grid(row=1, column=2, sticky=NSEW, padx=2, pady=2)
        frame.columnconfigure(0, weight=1)

        typeframe = Frame(frame, relief=GROOVE, borderwidth=1, padx=2, pady=2)
        typeframe.grid(row=0, column=0, sticky=NSEW)
        label = Label(typeframe, text='Entry Type')
        label.grid(row=0, column=0, sticky=W)

        buttonframe = Frame(typeframe, padx=5, pady=5)
        buttonframe.grid(row=1, column=0, sticky=NSEW)
        self.typebuttons = []
        self.typevar = StringVar()
        self.typevar.set(EntryType.NONE.name)
        self.typevar.trace('w', self._typeChanged)

        index = 0
        for et in EntryType:
            self._addEntryTypeButton(buttonframe, index, et)
            index += 1

        colorframe = Frame(frame, relief=GROOVE, borderwidth=1, padx=2, pady=2)
        colorframe.grid(row=1, column=0, sticky=NSEW, pady=3)
        label = Label(colorframe, text='Highlight Color')
        label.grid(row=0, column=0, sticky=W)

        buttonframe = Frame(colorframe, padx=5, pady=5)
        buttonframe.grid(row=1, column=0, sticky=NSEW)
        self.colorbuttons = []
        self.colorvar = StringVar()
        self.colorvar.set(EntryColors.DEFAULT.name)
        self.colorvar.trace('w', self._colorChanged)

        index = 0
        for color in EntryColors:
            self._addColorButton(buttonframe, index, color)
            index += 1

        self.lastentry = Content.editEntry
        self._rebuildPage()
    
    def _typeChanged(self, *args):
        if self.typevar.get() == ' ':
            return
        newtype = EntryType[self.typevar.get()]
        if self.lastentry.entrytype != newtype:
            self.lastentry.entrytype = newtype
            self.lastentry.modified = True
            Content.contentMutated()

    def _addEntryTypeButton(self, master, index, et):
        button = Radiobutton(master, text=et.value, variable=self.typevar, value=et.name)
        button.grid(row=index, column=0, sticky=W)
        self.typebuttons.append(button)

    def _colorChanged(self, *args):
        if self.colorvar.get() == ' ':
            return
        newtype = EntryColors[self.colorvar.get()]
        if self.lastentry.entrycolor != newtype:
            self.lastentry.entrycolor = newtype
            Content.contentMutated()
    
    def _addColorButton(self, master, index, color):
        if color == EntryColors.DEFAULT:
            button = Radiobutton(master, text='None', variable=self.colorvar, value=color.name)
        else:
            button = Radiobutton(master, bg=color.value, activebackground=color.value, variable=self.colorvar, value=color.name, width=10, anchor=W)
        button.grid(row=index, column=0, sticky=W)
        self.colorbuttons.append(button)

    def refreshView(self):
        if self.lastentry != Content.editEntry:
            self.lastentry = Content.editEntry
            self._rebuildPage()
    
    def _rebuildPage(self):
        if self.lastentry == None:
            self.typevar.set(' ')
            self.colorvar.set(' ')
            for button in self.typebuttons:
                button.config(state=DISABLED)
            for button in self.colorbuttons:
                button.config(state=DISABLED)
        else:
            self.typevar.set(self.lastentry.entrytype.name)
            self.colorvar.set(self.lastentry.entrycolor.name)
            for button in self.typebuttons:
                button.config(state=NORMAL)
            for button in self.colorbuttons:
                button.config(state=NORMAL)
