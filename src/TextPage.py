import tkinter
from tkinter import *
from tkinter import messagebox
from TextModified import TextModified
from DialogueData import Page

# TODO Text box right click
# TODO Text box copy paste

_WRAP_WIDTH = 37 # From the game
_WRAP_HEIGHT = 7 # From the game
_BUTTON_WIDTH = 5 # Width of buttons

class TextPage(tkinter.Frame):
    def __init__(self, page, index, rebuildcommand, master=None, cnf={}, **kw):
        tkinter.Frame.__init__(self, master, cnf, **kw)
        self.config(padx=5,pady=5)
        self.master = master

        self.page = page
        self.index = index
        self.rebuildcommand = rebuildcommand

        content = 'Lorem Ipsum Dolor Est'
        if page:
            content = page.content
        
        self.detaillabel = Label(self)
        self.detaillabel.grid(row=0, column=0, sticky=W)

        self.pageEditPane = TextModified(self, wrap=WORD, width=_WRAP_WIDTH, height=_WRAP_HEIGHT)
        self.pageEditPane.insert(END, content)
        self.pageEditPane.grid(row=1, column=0, sticky=NW)
        self.pageEditPane.bind('<<TextModified>>', self._pageModified)

        buttonframe = Frame(self, pady=5)
        buttonframe.grid(row=2, column=0, sticky=NSEW)
        buttonframe.columnconfigure(1, weight=1)

        self.addButtonleft = Button(buttonframe, text='<+', width=_BUTTON_WIDTH, command=self._addPageLeft)
        self.addButtonleft.grid(row=0, column=0, sticky=W)

        self.buttonDelete = Button(buttonframe, text='X', width=_BUTTON_WIDTH, command=self._deletePage)
        self.buttonDelete.grid(row=0, column=1)

        self.addbuttonright = Button(buttonframe, text='+>', width=_BUTTON_WIDTH, command=self._addPageRight)
        self.addbuttonright.grid(row=0, column=2, sticky=E)

        self._updateDetails()
    
    def _pageModified(self, event):
        pane = self.pageEditPane.get('1.0',END).rstrip()
        self.page.content = pane
        self._updateDetails()

    def _updateDetails(self):
        if self.page:
            self.detaillabel.config(text='Page ' + str(self.index + 1) + '\tChars: ' + str(len(self.page.content.rstrip())))
    
    def _deletePage(self):
        if len(self.page.parent.getPages()) < 2:
            # We can't delete the last page
            return
        text = 'Text: [Empty]'
        if len(self.page.content) > 0:
            text = 'Text: \"' + self.page.content + '\"'
        if messagebox.askyesno(
                'Delete Page?', 
                'Are you sure you want to delete page ' + str(self.index + 1) + ' from entry \"' + self.page.parent.parent.getPath() + '\"?\n\n' + text,
                default=messagebox.NO
            ):
                self.page.parent.getPages().pop(self.index)
                self.rebuildcommand()

    def _addPageLeft(self):
        self.page.parent.addPage(self.index)
        self.rebuildcommand()

    def _addPageRight(self):
        self.page.parent.addPage(self.index + 1)
        self.rebuildcommand()
    
    def width(self):
        return self.winfo_reqwidth()

    def height(self):
        return self.winfo_reqheight()