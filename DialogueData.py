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
        self.sortNodes()
        return node
    
    def addEntry(self, id, entrytype=EntryType.NONE):
        result = DialogueEntry(id, entrytype, self)
        self.entries.append(result)
        self.sortEntries()
        return result
    
    def sortNodes(self):
        self.children.sort(key=lambda x: x.id)

    def sortEntries(self):
        self.entries.sort(key=lambda x: x.id)

    def getPath(self):
        # No path if we're the root
        if self.parent == None:
            return ''
        result = self.id
        parent = self.parent
        while parent != None:
            if parent.parent == None:
                break
            # Don't include the root Content
            result = parent.id + '.' + result
            parent = parent.parent
        return result
    
    # Only works when called from the root!
    def findNode(self, path):
        # If we're caling this from the root, looking for the root, you found it!
        if len(path) < 1:
            return self
        return self._searchForNode(path.split('.'))
    
    def _searchForNode(self, path):
        # If we found the end of the path
        if len(path) < 1:
            return self
        section = path.pop(0)
        # Search down the list
        for child in self.children:
            if child.id == section:
                return child._searchForNode(path)
        # If we don't have a child of that name, wefound the path
        return self
    
    def findEntry(self, path):
        node = self.findNode(path)
        entryname = path.split('.').pop()
        for entry in node.entries:
            if entry.id == entryname:
                return entry
        # This really shouldn't happen!
        return None