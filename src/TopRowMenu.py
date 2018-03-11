from tkinter import *
from Content import Content
from PopupDialog import PopupDialog
from Consts import ValidateResult, nameblacklistcsharp, validateName

newid = '[New]'

class TopRowMenu:
    def __init__(self, master):
        self.master = master

        self.frame = Frame(master)
        self.frame.grid(row=0, column=0, sticky=NSEW)

        self.regionstring = StringVar()
        self.regionstring.set(Content.region)

        label = Label(self.frame, text='Region:')
        label.grid(row=0, column=0, sticky=E)

        self.entryLabel = Label(master, text='Text')
        self.entryLabel.grid(row=0, column=1, sticky=W, columnspan=2)

        self.option = None
        self._rebuildOptions()
        self._updateEntryText()
    
    def refreshView(self):
        self.regionstring.set(Content.region)
        self._rebuildOptions()
        self._updateEntryText()

    def _updateEntryText(self):
        if Content.editEntry == None:
            self.entryLabel.config(text='No Entry Selected')
            return
        self.entryLabel.config(text='Entry: ' + Content.editEntry.getPath())        
    
    def _rebuildOptions(self):
        if self.option:
            self.option.destroy()
        regioncontent = Content.allregions[:]
        regioncontent.append(newid)
        self.option = OptionMenu(self.frame, self.regionstring, *regioncontent, command=self._selectRegion)
        self.option.grid(row=0, column=1, sticky=W)
    
    def _selectRegion(self, region):
        if region == newid:
            self.regionstring.set(Content.region)
            popup = PopupDialog(self.master, title='New Region Id', label='Id:', validate=self._validateRegion)
            if popup.result:
                Content.region = popup.result
                Content.allregions.append(popup.result)                
                self.regionstring.set(Content.region)
                self._rebuildOptions()
                Content.contentMutated()
            return
        if region != Content.region:
            Content.region = region
            Content.contentMutated()

    def _validateRegion(self, name):
        for id in Content.allregions:
            if id == name:
                return ValidateResult.NAME_CONFLICT
        return validateName(name)
