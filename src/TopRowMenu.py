from tkinter import *
from DialogueContent import DialogueContent
from SimpleDialog import Dialog

class TopRowMenu:
    def __init__(self, master, content=DialogueContent):
        self.content = content

        self.regionContent = DialogueContent.allregions[:]
        self.regionContent.append('New')

        self.regionstring = StringVar()
        self.regionstring.set(DialogueContent.region)

        label = Label(master, text='Region:')
        label.grid(row=0, column=0, sticky=E)

        option = OptionMenu(master, self.regionstring, *self.regionContent, command=self._selectRegion)
        option.grid(row=0, column=1, sticky=W)
    
    def _selectRegion(self, region):
        if region == 'New':
            # TODO create a new one
            print('New Region')
            self.regionstring.set(DialogueContent.region)
            return
        if region != DialogueContent.region:
            DialogueContent.region = region
            self.content.contentMutated()
