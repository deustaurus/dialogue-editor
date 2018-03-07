import re
import string
from data.DialogueData import DialogueGroup, EntryType

# TODO undo tree?
# TODO modified flags

class DialogueContent:
    def __init__(self):
        # Editing Content
        self.editEntry = None

        self.mutateEvent = []

        # Dummy Content
        self.data = DialogueGroup('Content')
        common = self.data.addNode('Common10')
        common.addNode('Common10')
        common.addEntry('Chum')
        common.addEntry('Crum_1')
        common.addEntry('Crum_10')
        common.addEntry('Crum_100')
        common.addEntry('Crum_200')
        common.addEntry('Crum_2')
        common.addEntry('Blum')
        common.addEntry('Cram', EntryType.DIARY)
        table = common.addNode('Common 1')
        table.addEntry('Zome', EntryType.DIARY)
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
