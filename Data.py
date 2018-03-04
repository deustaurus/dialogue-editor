from enum import Enum

class EntryType(Enum):
    NONE = 'Default'
    DIARY = 'Diary'

class DialogueEntry:
    def __init__(self, id, entrytype, parent):
        self.parent = parent
        self.id = id
        self.entrytype = entrytype
        self.pages = []
    
    def getPath(self):
        return self.parent.getPath() + '.' + self.id

class DialogueNode:
    def __init__(self, id, parent=None):
        self.parent = parent
        self.id = id
        self.children = []
        self.entries = []
    
    def addNode(self, id):
        node = DialogueNode(id, self)
        self.children.append(node)
        self.children.sort(key=lambda x: x.id)
        return node
    
    def addEntry(self, id, entrytype=EntryType.NONE):
        self.entries.append(DialogueEntry(id, entrytype, self))
        self.entries.sort(key=lambda x: x.id)

    def getPath(self):
        result = self.id
        parent = self.parent
        while parent != None:
            if parent.parent == None:
                break
            # Don't include the root Content
            result = parent.id + '.' + result
            parent = parent.parent
        return result