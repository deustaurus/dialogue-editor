from tkinter import *
from tkinter import ttk
from data.DialogueContent import DialogueContent
from widget.TextModified import TextModified
from enum import Enum
from views.EntryPage import EntryPage

# TODO scroll canvas

class EntryState(Enum):
    INVALID = 0
    VALID = 1

class EntryPanel:
    def __init__(self, master, content=DialogueContent):
        self.master = master
        self.content = content

        # Take the right half of the window
        panelFrame = Frame(master)
        panelFrame.grid(row=0, column=1, sticky=NSEW)
        panelFrame.columnconfigure(0, weight=1)
        panelFrame.rowconfigure(1, weight=1)

        # Frame for detail readouts
        detailsFrame = Frame(panelFrame)
        detailsFrame.grid(row=0, column=0, sticky=NSEW)

        # Frame for canvas
        canvasFrame = Frame(panelFrame)
        canvasFrame.grid(row=1, column=0, sticky=NSEW)
        canvasFrame.rowconfigure(0, weight=1)
        canvasFrame.columnconfigure(0, weight=1)

        # # Calculate initial width of widgets
        testpage = EntryPage(None, 0, canvasFrame)
        testpage.grid(row=0, column=0)
        master.update_idletasks()
        self.panelwidgetwidth = testpage.width()
        self.panelwidgetheight = testpage.height()
        testpage.destroy()

        # # Put canvas in frame
        self.canvas = Canvas(canvasFrame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=NSEW)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.width = self.canvas.winfo_reqwidth()
        self.canvas.height = self.canvas.winfo_reqheight()
        self.canvas.rowconfigure(0, weight=1)
        self.canvas.columnconfigure(0, weight=1)

        # Put final scrolling content frame in canvas
        self.contentFrame = Frame(self.canvas)
        self.contentFrame.grid(row=0, column=0, sticky=NSEW)

        # Hook up the scroll bar next to the canvas
        yscroll = ttk.Scrollbar(canvasFrame, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky=NS)
        self.canvas.create_window((0,0), window=self.contentFrame, anchor=NW)

        # TODO Add detail labels here
        self.labeltitle = Label(detailsFrame, text='')
        self.labeltitle.grid(row=0, column=0)

        self.editpages = []
        self.lastentry = None

    def on_resize(self, event):
        if self.canvas.width == event.width and self.canvas.height == event.height:
            # If no change, don't layout again
            return
        self.canvas.width = event.width
        self.canvas.height = event.height
        self._layoutPages()

    def refreshView(self):
        self._rebuildPage()
    
    def _rebuildPage(self):
        if self.lastentry != self.content.editEntry:
            while len(self.editpages) > 0:
                self.editpages.pop().destroy()
            self.lastentry = self.content.editEntry
            if self.lastentry:
                for index in range(0, len(self.lastentry.pages)):
                    editpane = EntryPage(self.lastentry.pages[index], index, self.contentFrame)
                    self.editpages.append(editpane)
        self._layoutPages()

    def _layoutPages(self):
        if self.lastentry == None:
            self.labeltitle.config(text='No Entry Selected')
            return
        self.labeltitle.config(text='Entry: ' + self.lastentry.getPath())

        accumwidth = 0
        accumheight = self.panelwidgetheight
        row = 0
        column = 0

        for page in self.editpages:
            if accumwidth + self.panelwidgetwidth > self.canvas.width and column > 0:
                accumwidth = 0
                column = 0
                row += 1
                accumheight += self.panelwidgetheight
            page.grid(row=row, column=column, sticky=NW)            
            column += 1
            accumwidth += self.panelwidgetwidth
        
        scroll = (0,0,self.canvas.width,max(accumheight,self.canvas.height))
        self.canvas.configure(
            scrollregion=scroll,
            width=self.canvas.width,
            height=self.canvas.height
        )
