import string
from enum import Enum
from tkinter import *
from tkinter import ttk, messagebox
from DialogueContent import DialogueContent
from SimpleDialog import Dialog
from Consts import nameblacklistcsharp, ValidateResult

# TODO tag entries with color
# TODO keyboard commands

class DragState(Enum):
    NONE = 0
    DRAG = 1
    SUCCESS = 2

class DialogueTree:
    def __init__(self, master, content=DialogueContent):
        self.master = master
        self.content = content

        self.dragstate = DragState.NONE
        self.treeselection = None
        self.verifynode = None

        outerFrame = Frame(master)
        outerFrame.grid(row=0, column=0, sticky=NSEW)
        outerFrame.columnconfigure(0, weight=1)
        outerFrame.rowconfigure(1, weight=1)
        
        topFrame = Frame(outerFrame, padx=5, pady=5)
        topFrame.grid(row=0, column=0, sticky=W)

        treeFrame = Frame(outerFrame)
        treeFrame.grid(row=1, column=0, sticky=NSEW)

        self._createTree(treeFrame)
        self._createRightClickMenu(outerFrame)

        self._setupButtons(None)

    def _createTree(self, master):
        dataCols = ('group', 'type', 'pages')
        self.tree = ttk.Treeview(columns=dataCols, displaycolumns=['type','pages'], selectmode='browse')
        yscroll = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        self.tree['yscroll'] = yscroll.set

        self.tree.heading('#0', text='Dialogue Tree', anchor=W)
        self.tree.heading('type', text='Type', anchor=W)
        self.tree.heading('pages', text='Pages', anchor=W)
        self.tree.column('#0', stretch=0, width=300)
        self.tree.column('type', stretch=0, width=70)
        self.tree.column('pages', stretch=0, width=50)

        self.tree.grid(in_=master, row=0, column=0, sticky=NSEW)
        yscroll.grid(in_=master, row=0, column=1, sticky=NS)

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self._treeSelect)
        self.tree.bind('<Button-3>', self._rightClickTree)
        self.tree.bind("<ButtonPress-1>", self._leftClickTree)
        self.tree.bind("<ButtonRelease-1>", self._leftClickTreeRelease, add='+')
        self.tree.bind("<B1-Motion>", self._leftClickTreeMove, add='+')
        self.tree.bind('<Double-1>', self._doubleClickTree)

    def _createRightClickMenu(self, master):
        self.popupmenu = Menu(master, tearoff=0)

        self.popupmenu.add_command(label='New Group', command=self._actionNewGroup)
        self.popupmenu.add_command(label='New Entry', command=self._actionNewEntry)
        self.popupmenu.add_command(label='Duplicate Id', command=self._actionDuplicate)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Rename', command=self._actionRename)
        self.popupmenu.add_separator()
        self.popupmenu.add_command(label='Delete', command=self._actionDelete)

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
        if len(name) < 1:
            return ValidateResult.LENGTH
        if name in nameblacklistcsharp:
            return ValidateResult.RESERVED_NAME
        return ValidateResult.SUCCESS

    def _validateGroup(self, name):
        for node in self.verifynode.children:
            if node.id == name:
                return ValidateResult.NAME_CONFLICT
        return self._validateName(name)
    
    def _validateEntry(self, name):
        for entry in self.verifynode.entries:
            if entry.id == name:
                return ValidateResult.NAME_CONFLICT
        return self._validateName(name)

    def _actionNewGroup(self):
        self.verifynode = self.content.data.findNode(self.treeselection[0])
        popup = Dialog(self.master, "New Group", validate=self._validateGroup)
        if popup.result:
            result = self.verifynode.addNode(popup.result)
            self.content.contentMutated()
            iid = self._findTreeIndexByPath(result.parent.getPath())
            if iid:
                self.tree.item(iid, open=YES)
                iid = self._findTreeIndexByPath(result.getPath())
                if iid:
                    self.tree.selection_set(iid)
    
    def _actionNewEntry(self):
        self.verifynode = self.content.data.findNode(self.treeselection[0])
        popup = Dialog(self.master, "New Entry", validate=self._validateEntry)
        if popup.result:
            entry = self.verifynode.addEntry(popup.result)
            self.content.editEntry = entry
            self.content.contentMutated()
            iid = self._findTreeIndexByPath(entry.parent.getPath())
            if iid:
                self.tree.item(iid, open=YES)
                iid = self._findTreeIndexByPath(entry.getPath())
                if iid:
                    self.tree.selection_set(iid)
    
    def _actionRename(self):
        renametype = self.treeselection[3]
        if renametype == 'group':
            node = self.content.data.findNode(self.treeselection[0])
            self.verifynode = node.parent
            popup = Dialog(self.master, 'Rename Group', inittext=node.id, validate=self._validateGroup)
            if popup.result:
                openstate = self.tree.item(self.tree.selection())['open']
                node.id = popup.result
                node.parent.sortNodes()
                self.content.contentMutated()
                iid = self._findTreeIndexByPath(node.getPath())
                if iid:
                    self.tree.selection_set(iid)
                    self.tree.item(iid, open=openstate)
        elif renametype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            self.verifynode = entry.parent
            popup = Dialog(self.master, 'Rename Entry', inittext=entry.id, validate=self._validateEntry)
            if popup.result:
                entry.id = popup.result
                entry.parent.sortEntries()
                self.content.contentMutated()
                iid = self._findTreeIndexByPath(entry.getPath())
                if iid:
                    self.tree.selection_set(iid)

    def _actionDelete(self):
        deletetype = self.treeselection[3]
        if deletetype == 'group':
            node = self.content.data.findNode(self.treeselection[0])
            countchildren = node.countChildren() + 1
            countentries = node.countEntries()
            countpages = node.countPages()
            message = 'Are you sure you want to delete \"' + node.id + '\"?\n\n'
            message += str(countchildren) + ' group(s) will be deleted containing '
            message += str(countentries) + ' entries and '
            message += str(countpages) + ' page(s).'
            if messagebox.askyesno(
                'Delete Node?', 
                message,
                default=messagebox.NO
            ):
                node.parent.children.remove(node)
        elif deletetype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            if messagebox.askyesno(
                'Delete Entry?',
                'Are you sure you want to delete \"' + entry.id + '\"?\n\n' + str(len(entry.pages)) + ' page(s) will be deleted.',
                default=messagebox.NO
            ):
                entry.parent.entries.remove(entry)
        self.content.contentMutated()
    
    def _actionDuplicate(self):
        duplicatetype = self.treeselection[3]
        if duplicatetype == 'group':
            node = self.content.data.findNode(self.treeselection[0])
            self.verifynode = node.parent
            node.parent.addNode(self._incrementName(node.id, self._validateGroup))
        elif duplicatetype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            self.verifynode = entry.parent
            entry.parent.addEntry(self._incrementName(entry.id, self._validateEntry))
        self.content.contentMutated()

    def _treeSelect(self, event):
        iid = self.tree.selection()
        self._setupButtons(iid)

    def _rightClickTree(self, event):
        # Clear any drag state
        self.dragstate = DragState.NONE
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                self.tree.selection_set(iid)
                self.popupmenu.tk_popup(event.x_root + 50, event.y_root + 10, 0)
            finally:
                self.popupmenu.grab_release()
        else:
            self.tree.selection_set()
    
    def _setupButtons(self, iid):
        if not iid:
            self.popupmenu.entryconfig(0, state=DISABLED) # New Group
            self.popupmenu.entryconfig(1, state=DISABLED) # New Entry
            self.popupmenu.entryconfig(2, state=DISABLED) # Duplicate
            self.popupmenu.entryconfig(4, state=DISABLED) # Rename
            self.popupmenu.entryconfig(6, state=DISABLED) # Delete
            return
        # Default settings, group mode
        self.popupmenu.entryconfig(0, state=ACTIVE) # New Group
        self.popupmenu.entryconfig(1, state=ACTIVE) # New Entry
        self.popupmenu.entryconfig(2, state=ACTIVE) # Duplicate
        self.popupmenu.entryconfig(4, state=ACTIVE) # Rename
        self.popupmenu.entryconfig(6, state=ACTIVE) # Delete
        # Get information
        # self.tree.selection_set(iid)
        self.treeselection = self._getItemValuesByTreeId(iid)
        seltype = self.treeselection[3]
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

    def _leftClickTree(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self._setupButtons(iid)
            val = self._getItemValuesByTreeId(iid)
            if val[3] == 'root' or val[3] == 'empty':
                # We don't allow dragging of the root, of course!
                return
            self.dragstate = DragState.DRAG
            self.treeselection = self._getItemValuesByTreeId(iid)

    def _leftClickTreeRelease(self, event):
        if self.dragstate != DragState.NONE:
            if self.dragstate == DragState.SUCCESS:
                newparent = self.content.data.findNode(self._getItemPathByTreeId(self.tree.selection()))
                movetype = self.treeselection[3]
                if movetype == 'group':
                    moveitem = self.content.data.findNode(self.treeselection[0])
                    moveitem.parent.children.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.children.append(moveitem)
                    newparent.sortNodes()
                elif movetype == 'entry':
                    moveitem = self.content.data.findEntry(self.treeselection[0])
                    moveitem.parent.entries.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.entries.append(moveitem)
                    newparent.sortEntries()
                self.content.contentMutated()
                self.tree.item(self._findTreeIndexByPath(newparent.getPath()), open=YES)
                self.tree.selection_set(self._findTreeIndexByPath(moveitem.getPath()))
            else:
                # If we didn't succeed, reset the selection back to the start
                self.tree.selection_set(self._findTreeIndexByPath(self.treeselection[0]))
            self.dragstate = DragState.NONE

    def _leftClickTreeMove(self, event):
        if self.dragstate == DragState.NONE:
            # If we're not in the drag state, we don't do the drag
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self.dragstate = DragState.DRAG
            movepath = self._getItemPathByTreeId(iid)
            self.verifynode = self.content.data.findNode(movepath)
            currentpath = self.content.getItemPathByString(self.treeselection[0])
            # First check what type of move we're doing
            movetype = self.treeselection[3]
            if movetype == 'group':
                node = self.content.data.findNode(self.treeselection[0])
                # We can't drag a group inside itself, so welook up the verify node's parents
                parent = self.verifynode.parent
                while parent != None:
                    if parent == node:
                        self.tree.selection_set()
                        return
                    parent = parent.parent
                # Check for name duplication in parent
                if self._validateGroup(node.id) is not ValidateResult.SUCCESS:
                    self.tree.selection_set()
                    return
                # Group move
                parentpath = node.parent.getPath()
            elif movetype == 'entry':
                if len(movepath) < 1:
                    # Can't drag entries to root
                    self.tree.selection_set()
                    return
                entry = self.content.data.findEntry(self.treeselection[0])
                # Check for name duplication in parent
                if self._validateEntry(entry.id) is not ValidateResult.SUCCESS:
                    self.tree.selection_set()
                    return
                # Entry move
                parentpath = entry.parent.getPath()
            
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
            self.content.editEntry = self.content.data.findEntry(val[0])
            self.content.contentMutated()
    
    def _getItemValuesByTreeId(self, id):
        return self.tree.item(id)['values']
    
    def _getItemPathByTreeId(self, id):
        return self.content.getItemPathByString(self._getItemValuesByTreeId(id)[0])
    
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
        self._populateTree(self.content.data, '')
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
        self._setupButtons(self.tree.selection())
