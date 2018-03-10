from tkinter import *
from DialogueContent import DialogueContent
from SimpleDialog import Dialog
from Consts import ValidateResult, nameblacklistcsharp, validateName

# TODO delete region

newid = '[New]'

class TopRowMenu:
    def __init__(self, master, content=DialogueContent):
        self.master = master
        self.content = content

        self.regionstring = StringVar()
        self.regionstring.set(DialogueContent.region)

        label = Label(master, text='Region:')
        label.grid(row=0, column=0, sticky=E)

        self.option = None
        self._rebuildOptions()
    
    def refreshView(self):
        self.regionstring.set(DialogueContent.region)
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
            self.regionstring.set(DialogueContent.region)
            popup = Dialog(self.master, title='New Region Id', label='Id:', validate=self._validateRegion)
            if popup.result:
                DialogueContent.region = popup.result
                self.content.allregions.append(popup.result)                
                self.regionstring.set(DialogueContent.region)
                self._rebuildOptions()
                self.content.contentMutated()
            return
        if region != DialogueContent.region:
            DialogueContent.region = region
            self.content.contentMutated()

    def _validateRegion(self, name):
        for id in self.content.allregions:
            if id == name:
                return ValidateResult.NAME_CONFLICT
        return validateName(name)