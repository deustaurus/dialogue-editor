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

        # Dummy Content
        self.data = DialogueData.Group('Content')
        common = self.data.addNode('Common10')
        common.addNode('Common10')
        common.addEntry('Chum')
        common.addEntry('Crum_1')
        common.addEntry('Crum_10')
        common.addEntry('Crum_100')
        common.addEntry('Crum_200')
        common.addEntry('Crum_2')
        common.addEntry('Blum')
        common.addEntry('Cram', DialogueData.EntryType.DIARY)
        table = common.addNode('Common 1')
        table.addEntry('Zome', DialogueData.EntryType.DIARY)
        table.addNode('Grulb')
        trag = self.data.addNode('Common1')
        trag.addEntry('Bop')
        trag.addEntry('Lope')
        bome = self.data.addNode('Common2')
        bome.addEntry('Crunt')
        bome.addNode('Crome')

    def contentMutated(self):
        for func in self.mutateEvent:
            func()

    def getItemPathByString(self, string):
        return self.data.findNode(string).getPath()
