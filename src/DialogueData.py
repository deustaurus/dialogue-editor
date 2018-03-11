from enum import Enum
from tkinter import StringVar
from natsort import natsort_keygen, ns
from Content import Content

# TODO modified flags

class EntryType(Enum):
    NONE = 'Default'
    DIARY = 'Diary'

class EntryColors(Enum):
    DEFAULT = 'default'
    RED = '#ff8080',
    GREEN = '#63ff53',
    BLUE = '#8d9dff',
    YELLOW = '#fff94e'
    ORANGE = '#ff954e'
    BROWN = '#c98151'

class Group:
    def __init__(self, id, parent=None):
        self.id = id
        self.parent = parent
        self.children = []
        self.entries = []
        self.modified = False
    
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

    def deleteRegion(self, region):
        for entry in self.entries:
            entry.deleteRegion(region)
    
    def allEntries(self):
        res = []
        self._addEntries(res)
        return res
    
    def _addEntries(self, res):
        for entry in self.entries:
            res.append(entry)
        for child in self.children:
            child._addEntries(res)

class Entry:
    def __init__(self, id, entrytype=EntryType, parent=Group):
        self.id = id
        self.parent = parent
        self.entrytype = entrytype
        self.entrycolor = EntryColors.DEFAULT
        self._region = {}
        self.getRegion('en')
        self.modified = False
    
    def getPath(self):
        return self.parent.getPath() + '.' + self.id

    def getRegion(self, id):
        if id not in self._region:
            self._region[id] = Region(self, id)
        return self._region[id]

    def addPage(self, index=None):
        return self.getRegion(Content.region).addPage(index)
    
    def getPages(self):
        return self.getRegion(Content.region).pages
    
    def deleteRegion(self, region):
        self._region.pop(region, None)
    
    def getExportFlag(self):
        if self.entrytype == EntryType.DIARY:
            return 'r'
        return 'n'

class Region:
    def __init__(self, parent, id):
        self.parent = parent
        self.pages = [Page(self)]
        self.id = id

    def addPage(self, index=None):
        page = Page(self)
        if index is not None:
            self.pages.insert(index,page)
        else:
            # If we didn't apply an index, we just append
            self.pages.append(page)
        return page
    
    def clearPages(self):
        self.pages = []

    def combinedPages(self):
        res = ''
        index = 0
        for page in self.pages:
            if len(page.content) < 1:
                continue
            if index > 0:
                res += '%r' # Page split
            val = page.content.rstrip()
            val = val.replace('\n','\\n')
            val = val.replace('\t','\\t')
            res += val
            index += 1
        return res

class Page:
    def __init__(self, parent=Region):
        self.parent = parent
        self.content = ''
