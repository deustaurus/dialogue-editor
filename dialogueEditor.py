import os

from enum import Enum
from tkinter import *
from tkinter import ttk

class EntryType(Enum):
    NONE = 'Default'
    DIARY = 'Diary'

class DialogueEntry:
    def __init__(self, id, entrytype=EntryType.NONE):
        self.id = id
        self.entrytype = entrytype

class DialogueNode:
    def __init__(self, id):
        self.id = id
        self.children = []
        self.entries = []
    
    def addNode(self, id):
        node = DialogueNode(id)
        self.children.append(node)
        self.children.sort(key=lambda x: x.id)
        return node
    
    def addEntry(self, id, entrytype=EntryType.NONE):
        self.entries.append(DialogueEntry(id, entrytype))
        self.entries.sort(key=lambda x: x.id)

class DialogueEditor:
    def __init__(self, master):
        self.master = master
        master.title("Dialogue Editor")
        master.geometry("800x600")

        self._setupMenu(master)

        self.content = DialogueNode('Content')
        common = self.content.addNode('Common')
        common.addEntry('Chum')
        common.addEntry('Blum')
        common.addEntry('Cram', EntryType.DIARY)
        table = common.addNode('Table')
        table.addEntry('Zome', EntryType.DIARY)
        table.addNode('Grulb')
        trag = self.content.addNode('Trag')
        trag.addEntry('Bop')
        trag.addEntry('Lope')
        self.content.addNode('Bome')        

        treeFrame = Frame(master)
        treeFrame.grid(row=0, column=0, sticky=NSEW)

        entryFrame = Frame(master, width=300, background="#ff0000")
        entryFrame.grid(row=0, column=1, sticky=NSEW)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

        self._createTable(treeFrame)

    def test(self):
        print("Test")

    def _setupMenu(self, master):
        menubar = Menu(master)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.test)
        filemenu.add_command(label="Save", command=self.test)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo")
        editmenu.add_command(label="Redo")
        menubar.add_cascade(label="Edit", menu=editmenu)

        master.config(menu=menubar)

    def _createTable(self, master):
        self.dataCols = ('group', 'type')
        self.tree = ttk.Treeview(columns=self.dataCols, displaycolumns='type')
        yscroll = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(orient=HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = yscroll.set
        self.tree['xscroll'] = xscroll.set

        self.tree.heading('#0', text='Dialogue Tree', anchor=W)
        self.tree.heading('type', text='Type', anchor=W)
        self.tree.column('type', stretch=0, width=70)

        self.tree.grid(in_=master, row=0, column=0, sticky=NSEW)
        yscroll.grid(in_=master, row=0, column=1, sticky=NS)
        xscroll.grid(in_=master, row=1, column=0, sticky=EW)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewOpen>>', self._update_tree)
        self.tree.bind('<Button-3>', self.rightClick)
        self._populate_root()

    def _populate_root(self):
        self.tree.delete(*self.tree.get_children())
        for child in self.content.children:
            self._populate_tree(child, '')

    def _populate_tree(self, node, tree):
        treenode = self.tree.insert(tree, END, text=node.id, values=[node.id, ''])
        for child in node.children:
            self._populate_tree(child, treenode)
        if len(node.entries) > 0:
            for entry in node.entries:
                self.tree.insert(treenode, END, text=entry.id, values=[entry.id, entry.entrytype.value])
        else:
            self.tree.insert(treenode, END, text='[Empty]', values=['[Empty]', ''])
    
    def _update_tree(self, event): pass

    def rightClick(self, event):
        print('Right click!')

root = Tk()
app = DialogueEditor(root)
root.mainloop()