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
        self.pages = [DialoguePage(self)]
    
    def getPath(self):
        return self.parent.getPath() + '.' + self.id
    
    def addPage(self, index=None):
        page = DialoguePage(self)
        if index is not None:
            self.pages.insert(index,page)
        else:
            # If we didn't apply an index, we just append
            self.pages.append(page)
        return page

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

    def countChildren(self):
        # Pass num in an array so it's by ref
        num = [0]
        self._addCountChildren(num)
        return num[0]
    
    def _addCountChildren(self, num):
        num[0] += len(self.children)
        for child in self.children:
            child._addCountChildren(num)

    def countEntries(self):
        # Pass num in an array so it's by ref
        num = [0]
        self._addCountEntries(num)
        return num[0]

    def _addCountEntries(self, num):
        num[0] += len(self.entries)
        for child in self.children:
            child._addCountEntries(num)
    
    def countPages(self):
        # Pass num in an array so it's by ref
        num = [0]
        self._addCountPages(num)
        return num[0]
    
    def _addCountPages(self, num):
        for entry in self.entries:
            num[0] += len(entry.pages)
        for child in self.children:
            child._addCountPages(num)

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