import os

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from DialogueData import *
from Popup import Popup

# TODO make buttons for the right click menu stuff
# TODO some nice bg colors and stuff for list
# TODO add id duplicating
# TODO natural language alphabetic sorting
# TODO load from xml
# TODO save to xml

class DialogueEditor:
    def __init__(self, master):
        self.master = master
        master.title("Dialogue Editor")
        master.geometry("800x600")

        self._setupMenuBar(master)
        self._setupRightClick(master)

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
        bome = self.content.addNode('Bome')
        bome.addEntry('Crunt')
        bome.addNode('Crome')  

        treeFrame = Frame(master)
        treeFrame.grid(row=0, column=0, sticky=NSEW)

        entryFrame = Frame(master, width=300, background="#ff0000")
        entryFrame.grid(row=0, column=1, sticky=NSEW)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

        self._createTree(treeFrame)

    def test(self):
        print("Test")

    def _setupMenuBar(self, master):
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
    
    def _setupRightClick(self, master):
        self.popupmenu = Menu(master, tearoff=0)

        self.popupmenu.add_command(label='New Group', command=self._newGroupAction)
        self.popupmenu.add_command(label='New Entry', command=self._newEntryAction)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Rename', command=self._renameObject)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Delete', command=self._deleteObject)
    
    def _newGroupAction(self):
        node = self.content.findNode(self.treeSelection[0])
        popup = Popup(self.master, "New Group")
        if popup.result:
            # TODO This result must be validated!
            result = node.addNode(popup.result)
            self._populateTreeRoot()
            iid = self._findNode(result.parent.getPath())
            self.tree.item(iid, open=YES)
            iid = self._findNode(result.getPath())
            self.tree.selection_set(iid)
    
    def _newEntryAction(self):
        node = self.content.findNode(self.treeSelection[0])
        popup = Popup(self.master, "New Entry")
        if popup.result:
            # TODO This result must be validated!
            entry = node.addEntry(popup.result)
            self._populateTreeRoot()
            iid = self._findNode(entry.parent.getPath())
            self.tree.item(iid, open=YES)
            iid = self._findNode(entry.getPath())
            self.tree.selection_set(iid)
    
    def _renameObject(self):
        # TODO validate the changed name
        # TODO check for no change
        # TODO pre-populate the popup
        renametype = self.treeSelection[3]
        if renametype == 'group':
            node = self.content.findNode(self.treeSelection[0])
            popup = Popup(self.master, 'Rename Group')
            if popup.result:
                openstate = self.tree.item(self.tree.selection())['open']
                node.id = popup.result
                node.parent.sortNodes()
                self._populateTreeRoot()
                iid = self._findNode(node.getPath())
                self.tree.selection_set(iid)
                self.tree.item(iid, open=openstate)
        elif renametype == 'entry':
            entry = self.content.findEntry(self.treeSelection[0])
            popup = Popup(self.master, 'Rename Entry')
            if popup.result:
                entry.id = popup.result
                entry.parent.sortEntries()
                self._populateTreeRoot()
                iid = self._findNode(entry.getPath())
                self.tree.selection_set(iid)

    def _deleteObject(self):
        deletetype = self.treeSelection[3]
        if deletetype == 'group':
            node = self.content.findNode(self.treeSelection[0])
            # TODO Warn about how many children we're deleting?
            if messagebox.askyesno(
                'Delete Node?', 
                'Are you sure you want to delete \"' + node.id + '\"?', 
                default=messagebox.NO
            ):
                node.parent.children.remove(node)
                self._populateTreeRoot()
        elif deletetype == 'entry':
            entry = self.content.findEntry(self.treeSelection[0])
            # TODO Warn about how many pages we're deleting
            if messagebox.askyesno(
                'Delete Entry?',
                'Are you sure you want to delete \"' + entry.id + '\"?',
                default=messagebox.NO
            ):
                entry.parent.entries.remove(entry)
                self._populateTreeRoot()

    def _createTree(self, master):
        self.dataCols = ('group', 'type', 'pages')
        self.tree = ttk.Treeview(columns=self.dataCols, displaycolumns=['type','pages'], selectmode='browse')
        yscroll = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(orient=HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = yscroll.set
        self.tree['xscroll'] = xscroll.set

        self.tree.heading('#0', text='Dialogue Tree', anchor=W)
        self.tree.heading('type', text='Type', anchor=W)
        self.tree.heading('pages', text='Pages', anchor=W)
        self.tree.column('type', stretch=0, width=70)
        self.tree.column('pages', stretch=0, width=50)

        self.tree.grid(in_=master, row=0, column=0, sticky=NSEW)
        yscroll.grid(in_=master, row=0, column=1, sticky=NS)
        xscroll.grid(in_=master, row=1, column=0, sticky=EW)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.tree.bind('<Button-3>', self._rightClickTree)
        self._populateTreeRoot()

    def _cacheOpenState(self, treenode, openstate):
        children = self.tree.get_children(treenode)
        for child in children:
            self._cacheOpenState(child, openstate)
            item = self.tree.item(child)
            if item['open']:
                openstate.append(item['values'][0])

    def _applyOpenState(self, treenode, openstate):
        children = self.tree.get_children(treenode)
        for child in children:
            item = self.tree.item(child)
            key = item['values'][0]
            if key in openstate:
                self.tree.item(child, open=YES)
                openstate.remove(key)
            self._applyOpenState(child, openstate)
    
    def _findNode(self, name, treenode=None):
        children = self.tree.get_children(treenode)
        for child in children:
            item = self.tree.item(child)['values'][0]
            if item == name:
                return child
            childres = self._findNode(name, child)
            if childres:
                return childres
        # We shouldn't get here, but TODO handle this gracefully?
        return None

    def _populateTreeRoot(self):
        # Cache the whole tree state to preserve open states
        openstate = []
        self._cacheOpenState(None,openstate)

        self.tree.delete(*self.tree.get_children())
        self._populateTree(self.content, '')
        self.tree.item(self.tree.get_children(), open=YES)
        
        self._applyOpenState(None,openstate)

    def _populateTree(self, node, tree):
        nodetype = 'group'
        if node.parent == None:
            nodetype = 'root'
        treenode = self.tree.insert(tree, END, text=node.id, values=[node.getPath(), '', '', nodetype])

        # Show Entries
        for entry in node.entries:
            self.tree.insert(treenode, END, text=entry.id, values=[entry.getPath(), entry.entrytype.value, len(entry.pages), 'entry'])

        # Show children
        for child in node.children:
            self._populateTree(child, treenode)
        
        if len(node.entries) < 1 and len(node.children) < 1:
            self._addEmptyLine(treenode, node)


    def _addEmptyLine(self, treenode, node):
        self.tree.insert(treenode, 0, text='[Empty]', values=[node.getPath(), '', '', 'empty'])

    def _rightClickTree(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                # Default settings, group mode
                self.popupmenu.entryconfig(0, state=ACTIVE) # New Group
                self.popupmenu.entryconfig(1, state=ACTIVE) # New Entry
                self.popupmenu.entryconfig(3, state=ACTIVE) # Rename
                self.popupmenu.entryconfig(5, state=ACTIVE) # Delete
                # Get information
                self.tree.selection_set(iid)
                self.treeSelection = self.tree.item(iid)['values']
                seltype = self.treeSelection[3]
                # Check information
                if seltype == 'root':
                    # Root content can't be deleted, or have entries added
                    self.popupmenu.entryconfig(1, state=DISABLED)
                    self.popupmenu.entryconfig(3, state=DISABLED)
                    self.popupmenu.entryconfig(5, state=DISABLED)
                elif seltype == 'empty':
                    # You can't delete an empty object
                    self.popupmenu.entryconfig(3, state=DISABLED)
                    self.popupmenu.entryconfig(5, state=DISABLED)                    

                self.popupmenu.tk_popup(event.x_root + 50, event.y_root + 10, 0)
            finally:
                self.popupmenu.grab_release()
        else:
            self.tree.selection_set()

root = Tk()
app = DialogueEditor(root)
root.mainloop()