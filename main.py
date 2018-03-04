import os
import string
import re

from tkinter import *
from tkinter import ttk, messagebox
from DialogueData import *
from tkSimpleDialog import Dialog
from Consts import DragState

# TODO make buttons for the right click menu stuff
# TODO some nice bg colors and stuff for list
# TODO load from xml
# TODO save to xml

class DialogueEditor:

    def __init__(self, master):
        self.master = master
        master.title("Dialogue Editor")
        master.geometry("800x600")

        self.dragstate = DragState.NONE
        self.nodemodify = None
        self.entrymodify = None

        self._setupMenuBar(master)
        self._setupRightClick(master)

        self.content = DialogueNode('Content')
        common = self.content.addNode('Common 10')
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
        trag = self.content.addNode('Common1')
        trag.addEntry('Bop')
        trag.addEntry('Lope')
        bome = self.content.addNode('Common 2')
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
        self.popupmenu.add_command(label='Duplicate Id', command=self._duplicateIdAction)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Rename', command=self._renameObjectAction)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Delete', command=self._deleteObjectAction)

    def _incrementName(self, name, validation):
        num = 0
        match = re.match('.*?([0-9]+)$', name)
        if match:
            num = int(match.group(1))
        stripped = name.rstrip(string.digits)
        newname = stripped + str(num)
        while not validation(newname):
            num += 1
            newname = stripped + str(num)
        return newname

    def _validateName(self, name):
        return 1

    def _validateNewGroupName(self, name):
        for node in self.nodemodify.children:
            if node.id == name:
                return 0
        return self._validateName(name)

    def _validateRenameGroup(self, name):
        for node in self.nodemodify.parent.children:
            if node.id == name:
                return 0
        return self._validateName(name)
    
    def _validateNewEntryName(self, name):
        for entry in self.nodemodify.entries:
            if entry.id == name:
                return 0
        return self._validateName(name)
    
    def _validateRenameEntry(self, name):
        for entry in self.entrymodify.parent.entries:
            if entry.id == name:
                return 0
        return self._validateName(name)

    def _newGroupAction(self):
        self.nodemodify = self.content.findNode(self.treeSelection[0])
        popup = Dialog(self.master, "New Group", validate=self._validateNewGroupName)
        if popup.result:
            result = self.nodemodify.addNode(popup.result)
            self._populateTreeRoot()
            iid = self._findTreeIndexByPath(result.parent.getPath())
            self.tree.item(iid, open=YES)
            iid = self._findTreeIndexByPath(result.getPath())
            self.tree.selection_set(iid)
    
    def _newEntryAction(self):
        self.nodemodify = self.content.findNode(self.treeSelection[0])
        popup = Dialog(self.master, "New Entry", validate=self._validateNewEntryName)
        if popup.result:
            entry = self.nodemodify.addEntry(popup.result)
            self._populateTreeRoot()
            iid = self._findTreeIndexByPath(entry.parent.getPath())
            self.tree.item(iid, open=YES)
            iid = self._findTreeIndexByPath(entry.getPath())
            self.tree.selection_set(iid)
    
    def _renameObjectAction(self):
        renametype = self.treeSelection[3]
        if renametype == 'group':
            self.nodemodify = self.content.findNode(self.treeSelection[0])
            popup = Dialog(self.master, 'Rename Group', inittext=self.nodemodify.id, validate=self._validateRenameGroup)
            if popup.result:
                openstate = self.tree.item(self.tree.selection())['open']
                self.nodemodify.id = popup.result
                self.nodemodify.parent.sortNodes()
                self._populateTreeRoot()
                iid = self._findTreeIndexByPath(self.nodemodify.getPath())
                self.tree.selection_set(iid)
                self.tree.item(iid, open=openstate)
        elif renametype == 'entry':
            self.entrymodify = self.content.findEntry(self.treeSelection[0])
            popup = Dialog(self.master, 'Rename Entry', inittext=self.entrymodify.id, validate=self._validateRenameEntry)
            if popup.result:
                self.entrymodify.id = popup.result
                self.entrymodify.parent.sortEntries()
                self._populateTreeRoot()
                iid = self._findTreeIndexByPath(self.entrymodify.getPath())
                self.tree.selection_set(iid)

    def _deleteObjectAction(self):
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
    
    def _duplicateIdAction(self):
        duplicatetype = self.treeSelection[3]
        if duplicatetype == 'group':
            self.nodemodify = self.content.findNode(self.treeSelection[0])
            self.nodemodify.parent.addNode(self._incrementName(self.nodemodify.id, self._validateRenameGroup))
        elif duplicatetype == 'entry':
            self.entrymodify = self.content.findEntry(self.treeSelection[0])
            self.entrymodify.parent.addEntry(self._incrementName(self.entrymodify.id, self._validateRenameEntry))
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
        self.tree.bind("<ButtonPress-1>", self._leftClickTree)
        self.tree.bind("<ButtonRelease-1>", self._leftClickTreeRelease, add='+')
        self.tree.bind("<B1-Motion>", self._leftClickTreeMove, add='+')
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
            key = self._getItemValues(child)[0]
            if key in openstate:
                self.tree.item(child, open=YES)
                openstate.remove(key)
            self._applyOpenState(child, openstate)
    
    def _findTreeIndexByPath(self, path, treenode=None):
        children = self.tree.get_children(treenode)
        for child in children:
            if self._getItemValues(child)[0] == path:
                return child
            childres = self._findTreeIndexByPath(path, child)
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
    
    def _setItemOpen(self, id, openstate):
        self.tree.item(id, open=openstate)
    
    def _getItemValues(self, id):
        return self.tree.item(id)['values']

    def _getItemPathByTreeId(self, id):
        return self._getItemPathByString(self._getItemValues(id)[0])

    def _getItemPathByString(self, string):
        return self.content.findNode(string).getPath()

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
        # Show empty if there are no children or entries in a group
        if len(node.entries) < 1 and len(node.children) < 1:
            self.tree.insert(treenode, 0, text='[Empty]', values=[node.getPath(), '', '', 'empty'])

    def _rightClickTree(self, event):
        # Clear any drag state
        self.dragstate = DragState.NONE
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                # Default settings, group mode
                self.popupmenu.entryconfig(0, state=ACTIVE) # New Group
                self.popupmenu.entryconfig(1, state=ACTIVE) # New Entry
                self.popupmenu.entryconfig(2, state=ACTIVE) # Duplicate
                self.popupmenu.entryconfig(4, state=ACTIVE) # Rename
                self.popupmenu.entryconfig(6, state=ACTIVE) # Delete
                # Get information
                self.tree.selection_set(iid)
                self.treeSelection = self._getItemValues(iid)
                seltype = self.treeSelection[3]
                # Check information
                if seltype == 'root':
                    # Root content can't be deleted, or have entries added
                    self.popupmenu.entryconfig(1, state=DISABLED) # New Entry
                    self.popupmenu.entryconfig(2, state=DISABLED) # Duplicate
                    self.popupmenu.entryconfig(4, state=DISABLED) # Rename
                    self.popupmenu.entryconfig(6, state=DISABLED) # Delete
                elif seltype == 'empty':
                    # You can't delete an empty object
                    self.popupmenu.entryconfig(2, state=DISABLED) # Duplicate
                    self.popupmenu.entryconfig(4, state=DISABLED) # Rename
                    self.popupmenu.entryconfig(6, state=DISABLED) # Delete           

                self.popupmenu.tk_popup(event.x_root + 50, event.y_root + 10, 0)
            finally:
                self.popupmenu.grab_release()
        else:
            self.tree.selection_set()
    
    def _leftClickTree(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            val = self._getItemValues(iid)
            if val[3] == 'root' or val[3] == 'empty':
                # We don't allow dragging of the root, of course!
                return
            self.dragstate = DragState.DRAG
            self.treeSelection = self._getItemValues(iid)

    def _leftClickTreeRelease(self, event):
        if self.dragstate != DragState.NONE:
            if self.dragstate == DragState.SUCCESS:
                newparent = self.content.findNode(self._getItemPathByTreeId(self.tree.selection()))
                movetype = self.treeSelection[3]
                if movetype == 'group':
                    moveitem = self.content.findNode(self.treeSelection[0])
                    moveitem.parent.children.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.children.append(moveitem)
                    newparent.sortNodes()
                elif movetype == 'entry':
                    moveitem = self.content.findEntry(self.treeSelection[0])
                    moveitem.parent.entries.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.entries.append(moveitem)
                    newparent.sortEntries()
                self._populateTreeRoot()
            self.tree.selection_set()
            self.dragstate = DragState.NONE

    def _leftClickTreeMove(self, event):
        if self.dragstate == DragState.NONE:
            # If we're not in the drag state, we don't do the drag
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self.dragstate = DragState.DRAG
            movepath = self._getItemPathByTreeId(iid)
            currentpath = self._getItemPathByString(self.treeSelection[0])
            # First check what type of move we're doing
            movetype = self.treeSelection[3]
            if movetype == 'group':
                if self.treeSelection[0] in movepath:                    
                    # We can't drag a group inside itself
                    self.tree.selection_set()
                    return
                # Group move
                parentpath = self.content.findNode(self.treeSelection[0]).parent.getPath()
            elif movetype == 'entry':
                if len(movepath) < 1:
                    # Can't drag entries to root
                    self.tree.selection_set()
                    return
                # Entry move
                parentpath = self.content.findEntry(self.treeSelection[0]).parent.getPath()
            
            if parentpath == movepath or movepath == currentpath:
                self.tree.selection_set()
                return
            
            self.dragstate = DragState.SUCCESS
            iid = self._findTreeIndexByPath(movepath)
            self.tree.selection_set(iid)

root = Tk()
app = DialogueEditor(root)
root.mainloop()