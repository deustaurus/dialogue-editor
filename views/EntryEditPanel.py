from tkinter import *
from tkinter import ttk

# TODO another row to toggle the entry type

class EntryEditPanel:
    def __init__(self, master, main):
        self.master = master
        self.main = main

        entryFrame = Frame(master)
        entryFrame.grid(row=0, column=1, sticky=NSEW)

        entryButtonFrame = Frame(master, width=50)
        entryButtonFrame.grid(row=0, column=2, sticky=NSEW)

        self._createPageEdit(entryFrame)
        self._createPageButtons(entryButtonFrame)

    def _createPageEdit(self, master):
        contentcolumn = 2
        self.separatorLeft = ttk.Separator(master, orient=VERTICAL)
        self.separatorLeft.grid(row=0, column=0, rowspan=7, sticky=NS)
        self.separatorRight = ttk.Separator(master, orient=VERTICAL)
        self.separatorRight.grid(row=0, column=4, rowspan=7, sticky=NS)

        self.pageEditTitle = Label(master, text='Title', anchor=W)
        self.pageEditTitle.grid(row=1, column=contentcolumn, sticky=EW)
        self.pageEditEntryDetails = Label(master, text='Details', anchor=W)
        self.pageEditEntryDetails.grid(row=2, column=contentcolumn, sticky=EW)

        pageEditFrame = Frame(master)
        pageEditFrame.grid(row=4, column=contentcolumn, sticky=NSEW)
        self.pageEditPane = Text(pageEditFrame)
        self.pageEditPane.insert(END, 'Lorem ipsum dolor est')
        self.pageEditPane.grid(row=0, column=0, sticky=NSEW)        
        yscroll = ttk.Scrollbar(pageEditFrame, orient=VERTICAL, command=self.pageEditPane.yview)
        self.pageEditPane.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky=NS)
        pageEditFrame.columnconfigure(0, weight=1)
        pageEditFrame.rowconfigure(0, weight=1)

        self.pageEditDetails = Label(master, text='Page 1 Details', anchor=W)
        self.pageEditDetails.grid(row=5, column=contentcolumn, sticky=EW)

        master.rowconfigure(0, minsize=15) # Padding
        master.rowconfigure(4, weight=1)
        master.rowconfigure(6, minsize=15) # Padding
        master.columnconfigure(1, minsize=15) # Padding
        master.columnconfigure(contentcolumn, weight=1)
        master.columnconfigure(3, minsize=15) # Padding
    
    def _createPageButtons(self, master):
        # TODO These commands
        contentcolumn = 1
        textsize = 5
        padrows = [0,2,4,6,8,10,12,14]
        self.pagebuttons = []

        button = Button(master, text='Add', width=textsize)
        button.grid(row=1, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Rem', width=textsize)
        button.grid(row=3, column=contentcolumn)
        self.pagebuttons.append(button)
        
        separator = ttk.Separator(master)
        separator.grid(row=5, column=0, columnspan=5, sticky=EW)

        button = Button(master, text='First', width=textsize)
        button.grid(row=7, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Prev', width=textsize)
        button.grid(row=9, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Next', width=textsize)
        button.grid(row=11, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Last', width=textsize)
        button.grid(row=13, column=contentcolumn)
        self.pagebuttons.append(button)

        separator = ttk.Separator(master)
        separator.grid(row=15, column=0, columnspan=5, sticky=EW)
        
        master.columnconfigure(0, minsize=5)
        master.columnconfigure(2, minsize=5)
        for num in padrows:
            master.rowconfigure(num, minsize=15)
    
    def _populateEntryEditing(self):
        if self.main.editEntry == None:
            buttonstate = DISABLED
            self.pageEditTitle.config(text='No Entry Selected')
            self.pageEditEntryDetails.config(text='...')
            self._clearEditPane(DISABLED)
            self.pageEditDetails.config(text='...')
        else:
            buttonstate = ACTIVE
            currentpage = self.main.editEntry.editPage
            numpages = len(self.main.editEntry.pages)
            self.pageEditTitle.config(text='Editing Entry: ' + self.main.editEntry.getPath())
            self.pageEditEntryDetails.config(text='Page: ' + str(currentpage) + '/' + str(numpages))
            if currentpage >= numpages:
                self._clearEditPane(DISABLED)
                self.pageEditDetails.config(text='...')
        
        for button in self.pagebuttons:
            button.config(state=buttonstate)

    def _clearEditPane(self, nextstate):
        self.pageEditPane.config(state=NORMAL)
        self.pageEditPane.delete(1.0,END)
        self.pageEditPane.config(state=nextstate)