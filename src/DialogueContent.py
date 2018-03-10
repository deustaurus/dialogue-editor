import re
import string
import DialogueData

# TODO undo tree?
# TODO modified flags

class DialogueContent:

    # Static
    region = 'en'

    def __init__(self):
        # Editing Content
        self.editEntry = None

        self.mutateEvent = []
        self.allregions = ['en']

        # Dummy Content
        self.data = DialogueData.Group('Content')
        common = self.data.addGroup('Common10')
        common.addGroup('Common10')
        common.addEntry('Chum')
        common.addEntry('Crum_1')
        common.addEntry('Crum_10')
        common.addEntry('Crum_100')
        common.addEntry('Crum_200')
        common.addEntry('Crum_2')
        common.addEntry('Blum')
        common.addEntry('Cram', DialogueData.EntryType.DIARY)
        table = common.addGroup('Common 1')
        table.addEntry('Zome', DialogueData.EntryType.DIARY)
        table.addGroup('Grulb')
        trag = self.data.addGroup('Common1')
        trag.addEntry('Bop')
        trag.addEntry('Lope')
        bome = self.data.addGroup('Common2')
        bome.addEntry('Crunt')
        bome.addGroup('Crome')

    def contentMutated(self):
        for func in self.mutateEvent:
            func()

    def getItemPathByString(self, string):
        return self.data.findGroup(string).getPath()
    
    def clearRegions(self):
        self.allregions = []

    def deleteRegion(self, regionid):
        self.allregions.remove(regionid)
        DialogueContent.region = self.allregions[0]
        self.data.deleteRegion(regionid)
