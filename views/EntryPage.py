import tkinter
from tkinter import *
from widget.TextModified import TextModified

# TODO Text box right click
# TODO Text box copy paste

_WRAP_WIDTH = 37 # From the game
_WRAP_HEIGHT = 7 # From the game

class EntryPage(tkinter.Frame):
    def __init__(self, page, index, master=None, cnf={}, **kw):
        tkinter.Frame.__init__(self, master, cnf, **kw)
        self.config(padx=5,pady=5)
        self.master = master

        self.page = page
        self.index = index

        content = 'Lorem Ipsum Dolor Est'
        if page:
            content = page.content

        self.pageEditPane = TextModified(self, wrap=WORD, width=_WRAP_WIDTH, height=_WRAP_HEIGHT)
        self.pageEditPane.insert(END, content)
        self.pageEditPane.grid(row=0, column=0, sticky=NW)
        self.pageEditPane.bind('<<TextModified>>', self._pageModified)

        self.detaillabel = Label(self)
        self.detaillabel.grid(row=1, column=0, sticky=W)

        self._updateDetails()
    
    def _pageModified(self, event):
        pane = self.pageEditPane.get('1.0',END).rstrip()
        self.page.content = pane
        self._updateDetails()

    def _updateDetails(self):
        if self.page:
            self.detaillabel.config(text='Page ' + str(self.index + 1) + '\tChars: ' + str(len(self.page.content.rstrip())))
    
    def width(self):
        return self.winfo_reqwidth()

    def height(self):
        return self.winfo_reqheight()