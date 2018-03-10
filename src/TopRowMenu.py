from tkinter import *
from Content import Content
from PopupDialog import PopupDialog
from Consts import ValidateResult, nameblacklistcsharp, validateName

newid = '[New]'

class TopRowMenu:
    def __init__(self, master, content=Content):
        self.master = master
        self.content = content

        self.regionstring = StringVar()
        self.regionstring.set(Content.region)

        label = Label(master, text='Region:')
        label.grid(row=0, column=0, sticky=E)

        self.option = None
        self._rebuildOptions()
    
    def refreshView(self):
        self.regionstring.set(Content.region)
        self._rebuildOptions()
    
    def _rebuildOptions(self):
        if self.option:
            self.option.destroy()
        regioncontent = self.content.allregions[:]
        regioncontent.append(newid)
        self.option = OptionMenu(self.master, self.regionstring, *regioncontent, command=self._selectRegion)
        self.option.grid(row=0, column=1, sticky=W)
    
    def _selectRegion(self, region):
        if region == newid:
            self.regionstring.set(Content.region)
            popup = PopupDialog(self.master, title='New Region Id', label='Id:', validate=self._validateRegion)
            if popup.result:
                Content.region = popup.result
                self.content.allregions.append(popup.result)                
                self.regionstring.set(Content.region)
                self._rebuildOptions()
                self.content.contentMutated()
            return
        if region != Content.region:
            Content.region = region
            self.content.contentMutated()

    def _validateRegion(self, name):
        for id in self.content.allregions:
            if id == name:
                return ValidateResult.NAME_CONFLICT
        return validateName(name)