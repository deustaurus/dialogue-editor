from enum import Enum
from natsort import natsort_keygen, ns
from DialogueContent import DialogueContent

class EntryType(Enum):
    NONE = 'Default'
    DIARY = 'Diary'

class Group:
    def __init__(self, id, parent=None):
        self.id = id
        self.parent = parent
        self.children = []
        self.entries = []
    
    def addEntryPath(self, path):
        split = path.split('.')
        entryid = split.pop()
        group = self
        while len(split) > 0:
            group = self._findOrCreateGroup(group, split.pop(0))
        return group.addEntry(entryid)

    def _findOrCreateGroup(self, group, id):
        for child in group.children:
            if child.id == id:
                return child
        return group.addGroup(id)

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
            num[0] += len(entry.getPages())
        for child in self.children:
            child._addCountPages(num)

    def addGroup(self, id):
        group = Group(id, self)
        self.children.append(group)
        self.sortGroups()
        return group
    
    def addEntry(self, id, entrytype=EntryType.NONE):
        result = Entry(id, entrytype, self)
        self.entries.append(result)
        self.sortEntries()
        return result
    
    def sortGroups(self):
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
    def findGroup(self, path):
        # If we're caling this from the root, looking for the root, you found it!
        if len(path) < 1:
            return self
        return self._searchForGroup(path.split('.'))
    
    def _searchForGroup(self, path):
        # If we found the end of the path
        if len(path) < 1:
            return self
        section = path.pop(0)
        # Search down the list
        for child in self.children:
            if child.id == section:
                return child._searchForGroup(path)
        # If we don't have a child of that name, wefound the path
        return self
    
    def findEntry(self, path):
        group = self.findGroup(path)
        entryname = path.split('.').pop()
        for entry in group.entries:
            if entry.id == entryname:
                return entry
        return None

class Entry:
    def __init__(self, id, entrytype=EntryType, parent=Group):
        self.id = id
        self.parent = parent
        self.entrytype = entrytype
        self._region = {}
        self.getRegion('en')
    
    def getPath(self):
        return self.parent.getPath() + '.' + self.id

    def getRegion(self, id):
        if id not in self._region:
            self._region[id] = Region(self, id)
        return self._region[id]

    def addPage(self, index=None):
        return self.getRegion(DialogueContent.region).addPage(index)
    
    def getPages(self):
        return self.getRegion(DialogueContent.region).getPages()

class Region:
    def __init__(self, parent, id):
        self.parent = parent
        self._pages = [Page(self)]
        self.id = id
    
    def addPage(self, index=None):
        page = Page(self)
        if index is not None:
            self._pages.insert(index,page)
        else:
            # If we didn't apply an index, we just append
            self._pages.append(page)
        return page
    
    def getPages(self):
        return self._pages
    
    def clearPages(self):
        self._pages = []

class Page:
    def __init__(self, parent=Region):
        self.parent = parent
        self.content = ''
