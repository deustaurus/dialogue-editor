from enum import Enum
from tkinter import *
from tkinter import ttk

class DragState(Enum):
    NONE = 0
    DRAG = 1
    SUCCESS = 2

class DialogueTree:
    def __init__(self, master, main):
        self.master = master
        self.main = main

        self.dragstate = DragState.NONE

        treeFrame = Frame(master)
        treeFrame.grid(row=0, column=0, sticky=NSEW)

        self._createTree(treeFrame)
        self._createRightClickMenu(master)

    def _createTree(self, master):
        dataCols = ('group', 'type', 'pages')
        self.tree = ttk.Treeview(columns=dataCols, displaycolumns=['type','pages'], selectmode='browse')
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
        self.tree.bind('<Double-1>', self._doubleClickTree)

    def _createRightClickMenu(self, master):
        self.popupmenu = Menu(master, tearoff=0)

        self.popupmenu.add_command(label='New Group', command=self.main.newGroupAction)
        self.popupmenu.add_command(label='New Entry', command=self.main.newEntryAction)
        self.popupmenu.add_command(label='Duplicate Id', command=self.main.duplicateIdAction)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Rename', command=self.main.renameObjectAction)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Delete', command=self.main.deleteObjectAction)

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
                self.treeSelection = self._getItemValuesByTreeId(iid)
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
            val = self._getItemValuesByTreeId(iid)
            if val[3] == 'root' or val[3] == 'empty':
                # We don't allow dragging of the root, of course!
                return
            self.dragstate = DragState.DRAG
            self.treeSelection = self._getItemValuesByTreeId(iid)

    def _leftClickTreeRelease(self, event):
        if self.dragstate != DragState.NONE:
            if self.dragstate == DragState.SUCCESS:
                newparent = self.main.content.findNode(self._getItemPathByTreeId(self.tree.selection()))
                movetype = self.treeSelection[3]
                if movetype == 'group':
                    moveitem = self.main.content.findNode(self.treeSelection[0])
                    moveitem.parent.children.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.children.append(moveitem)
                    newparent.sortNodes()
                elif movetype == 'entry':
                    moveitem = self.main.content.findEntry(self.treeSelection[0])
                    moveitem.parent.entries.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.entries.append(moveitem)
                    newparent.sortEntries()
                self.main.refreshViews()
                self.tree.item(self._findTreeIndexByPath(newparent.getPath()), open=YES)
                self.tree.selection_set(self._findTreeIndexByPath(moveitem.getPath()))
            else:
                # If we didn't succeed, reset the selection back to the start
                self.tree.selection_set(self._findTreeIndexByPath(self.treeSelection[0]))
            self.dragstate = DragState.NONE

    def _leftClickTreeMove(self, event):
        if self.dragstate == DragState.NONE:
            # If we're not in the drag state, we don't do the drag
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self.dragstate = DragState.DRAG
            movepath = self._getItemPathByTreeId(iid)
            currentpath = self.main.getItemPathByString(self.treeSelection[0])
            # First check what type of move we're doing
            movetype = self.treeSelection[3]
            if movetype == 'group':
                if self.treeSelection[0] in movepath:                    
                    # We can't drag a group inside itself
                    self.tree.selection_set()
                    return
                # Group move
                parentpath = self.main.content.findNode(self.treeSelection[0]).parent.getPath()
            elif movetype == 'entry':
                if len(movepath) < 1:
                    # Can't drag entries to root
                    self.tree.selection_set()
                    return
                # Entry move
                parentpath = self.main.content.findEntry(self.treeSelection[0]).parent.getPath()
            
            if parentpath == movepath or movepath == currentpath:
                self.tree.selection_set()
                return
            
            iid = self._findTreeIndexByPath(movepath)
            if iid:
                self.dragstate = DragState.SUCCESS
                self.tree.selection_set(iid)
    
    def _doubleClickTree(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            # We really only respond to double clicking on entries
            val = self._getItemValuesByTreeId(iid)
            if val[3] != 'entry':
                return
            self.main.editEntry = self.main.content.findEntry(val[0])
            self.main.refreshViews()
    
    def _getItemValuesByTreeId(self, id):
        return self.tree.item(id)['values']
    
    def _getItemPathByTreeId(self, id):
        return self.main.getItemPathByString(self._getItemValuesByTreeId(id)[0])
    
    def _findTreeIndexByPath(self, path, treenode=None):
        children = self.tree.get_children(treenode)
        for child in children:
            if self._getItemValuesByTreeId(child)[0] == path:
                return child
            childres = self._findTreeIndexByPath(path, child)
            if childres:
                return childres
        return None

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
            key = self._getItemValuesByTreeId(child)[0]
            if key in openstate:
                self.tree.item(child, open=YES)
                openstate.remove(key)
            self._applyOpenState(child, openstate)

    def _populateTreeRoot(self):
        # Cache the whole tree state to preserve open states
        openstate = []
        self._cacheOpenState(None,openstate)
        self.tree.delete(*self.tree.get_children())
        self._populateTree(self.main.content, '')
        self.tree.item(self.tree.get_children(), open=YES)        
        self._applyOpenState(None,openstate)
    
    def _setItemOpen(self, id, openstate):
        self.tree.item(id, open=openstate)

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
    
    def refreshView(self):
        self._populateTreeRoot()