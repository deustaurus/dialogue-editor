from tkinter import *
from tkinter import ttk
from data.DialogueContent import DialogueContent
from widget.TextModified import TextModified
from enum import Enum

# TODO Text box right click
# TODO Text box copy paste

class EntryState(Enum):
    INVALID = 0
    VALID = 1

class EntryPanel:
    def __init__(self, master, content=DialogueContent):
        self.master = master
        self.content = content

        self.entrystate = EntryState.INVALID
        entryFrame = Frame(master)
        entryFrame.grid(row=0, column=1, sticky=NSEW)

        entryButtonFrame = Frame(master, width=50)
        entryButtonFrame.grid(row=0, column=2, sticky=NSEW)

        self._createPageEdit(entryFrame)
        self._createPageButtons(entryButtonFrame)

    def refreshView(self):
        self._populateEntryEditing()

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
        self.pageEditPane = TextModified(pageEditFrame)
        self.pageEditPane.insert(END, 'Lorem ipsum dolor est')
        self.pageEditPane.grid(row=0, column=0, sticky=NSEW)
        self.pageEditPane.bind('<<TextModified>>', self._pageModified)
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
        contentcolumn = 1
        textsize = 5
        padrows = [0,2,4,6,8,10,12,14]
        self.pagebuttons = []

        button = Button(master, text='Add', width=textsize, command=self._addPage)
        button.grid(row=1, column=contentcolumn)
        self.pagebuttons.append(button)

        # TODO Insert

        button = Button(master, text='Rem', width=textsize)
        button.grid(row=3, column=contentcolumn)
        self.pagebuttons.append(button)
        
        separator = ttk.Separator(master)
        separator.grid(row=5, column=0, columnspan=5, sticky=EW)

        button = Button(master, text='First', width=textsize, command=self._firstPage)
        button.grid(row=7, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Prev', width=textsize, command=self._prevPage)
        button.grid(row=9, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Next', width=textsize, command=self._nextPage)
        button.grid(row=11, column=contentcolumn)
        self.pagebuttons.append(button)

        button = Button(master, text='Last', width=textsize, command=self._lastPage)
        button.grid(row=13, column=contentcolumn)
        self.pagebuttons.append(button)

        separator = ttk.Separator(master)
        separator.grid(row=15, column=0, columnspan=5, sticky=EW)

        # TODO Toggle Type
        
        master.columnconfigure(0, minsize=5)
        master.columnconfigure(2, minsize=5)
        for num in padrows:
            master.rowconfigure(num, minsize=15)
    
    def _populateEntryEditing(self):
        self.entrystate = EntryState.INVALID
        if self.content.editEntry == None:
            buttonstate = DISABLED
            self.pageEditTitle.config(text='No Entry Selected')
            self.pageEditEntryDetails.config(text='...')
            self._clearEditPane(DISABLED)
            self.pageEditDetails.config(text='...')
        else:
            buttonstate = ACTIVE
            currentpage = self.content.editEntry.editPage + 1
            numpages = len(self.content.editEntry.pages)
            if numpages < 1:
                currentpage = 0
                self._clearEditPane(DISABLED)
            else:
                self._clearEditPane(NORMAL)
                self.pageEditPane.insert(END, self.content.editEntry.currentPage().content)
                # Pane entry is not enabled until now
                self.entrystate = EntryState.VALID
            self._updatePageEditDetails()
            self.pageEditTitle.config(text='Editing Entry: ' + self.content.editEntry.getPath())
            self.pageEditEntryDetails.config(text='Page: ' + str(currentpage) + '/' + str(numpages))
        
        for button in self.pagebuttons:
            button.config(state=buttonstate)

    def _clearEditPane(self, nextstate):
        self.pageEditPane.config(state=NORMAL)
        self.pageEditPane.delete(1.0,END)
        self.pageEditPane.config(state=nextstate)
    
    def _addPage(self):
        self.entrystate = EntryState.INVALID
        self.content.editEntry.addPage()
        self.content.editEntry.editPage = len(self.content.editEntry.pages) - 1
        self.content.contentMutated()
    
    def _firstPage(self):
        self.entrystate = EntryState.INVALID
        self.content.editEntry.editPage = 0
        self.content.contentMutated()
    
    def _prevPage(self):
        self.entrystate = EntryState.INVALID
        self.content.editEntry.editPage = max(self.content.editEntry.editPage - 1, 0)
        self.content.contentMutated()
    
    def _nextPage(self):
        self.entrystate = EntryState.INVALID
        self.content.editEntry.editPage = max(min(self.content.editEntry.editPage + 1, len(self.content.editEntry.pages) - 1), 0)
        self.content.contentMutated()
    
    def _lastPage(self):
        self.entrystate = EntryState.INVALID
        self.content.editEntry.editPage = max(len(self.content.editEntry.pages) - 1, 0)
        self.content.contentMutated()
    
    def _updatePageEditDetails(self):
        if self.content.editEntry:
            pagecontent = self.content.editEntry.currentPage()
            if pagecontent:
                self.pageEditDetails.config(text='Characters: ' + str(len(pagecontent.content)))
                return
        self.pageEditDetails.config(text='...')

    def _pageModified(self, event):
        if self.entrystate == EntryState.INVALID:
            return
        pane = self.pageEditPane.get('1.0',END).rstrip()
        self.content.editEntry.currentPage().content = pane
        self._updatePageEditDetails()