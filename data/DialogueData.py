from enum import Enum
from natsort import natsort_keygen, ns

# TODO add region

class EntryType(Enum):
    NONE = 'Default'
    DIARY = 'Diary'

class DialoguePage:
    def __init__(self, parent):
        self.parent = parent
        self.content = ''

class DialogueEntry:
    def __init__(self, id, entrytype, parent):
        self.id = id
        self.parent = parent
        self.entrytype = entrytype
        self.pages = []
        self.editPage = 0
    
    def getPath(self):
        return self.parent.getPath() + '.' + self.id
    
    def addPage(self):
        page = DialoguePage(self)
        self.pages.append(page)
        self.editPage = len(self.pages) - 1
        return page
    
    def currentPage(self):
        if len(self.pages) < 1:
            return None
        return self.pages[self.editPage]

class DialogueGroup:
    def __init__(self, id, parent=None):
        self.id = id
        self.parent = parent
        self.children = []
        self.entries = []
    
    def addEntryPath(self, path):
        split = path.split('.')
        entryid = split.pop()
        node = self
        while len(split) > 0:
            node = self._findOrCreateNode(node, split.pop(0))
        return node.addEntry(entryid)

    def _findOrCreateNode(self, node, id):
        for child in node.children:
            if child.id == id:
                return child
        return node.addNode(id)

    def addNode(self, id):
        node = DialogueGroup(id, self)
        self.children.append(node)
        self.sortNodes()
        return node
    
    def addEntry(self, id, entrytype=EntryType.NONE):
        result = DialogueEntry(id, entrytype, self)
        self.entries.append(result)
        self.sortEntries()
        return result
    
    def sortNodes(self):
        key = natsort_keygen(key=lambda x: x.id, alg=ns.IGNORECASE)
        self.children.sort(key=key)

    def sortEntries(self):
        key = natsort_keygen(key=lambda x: x.id, alg=ns.IGNORECASE)
        self.entries.sort(key=key)

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