import string
from enum import Enum
from tkinter import *
from tkinter import ttk, messagebox
from DialogueData import *
from Content import Content
from PopupDialog import PopupDialog
from Consts import nameblacklistcsharp, ValidateResult, validateName

# TODO tag entries with color
# TODO keyboard commands

class DragState(Enum):
    NONE = 0
    DRAG = 1
    SUCCESS = 2

class PanelTree:
    def __init__(self, master, content=Content):
        self.master = master
        self.content = content

        self.dragstate = DragState.NONE
        self.treeselection = None
        self.verifygroup = None

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

    def _validateGroup(self, name):
        for group in self.verifygroup.children:
            if group.id == name:
                return ValidateResult.NAME_CONFLICT
        return validateName(name)
    
    def _validateEntry(self, name):
        for entry in self.verifygroup.entries:
            if entry.id == name:
                return ValidateResult.NAME_CONFLICT
        return validateName(name)

    def _actionNewGroup(self):
        self.verifygroup = self.content.data.findGroup(self.treeselection[0])
        popup = PopupDialog(self.master, "New Group", validate=self._validateGroup)
        if popup.result:
            result = self.verifygroup.addGroup(popup.result)
            self.content.contentMutated()
            iid = self._findTreeIndexByPath(result.parent.getPath())
            if iid:
                self.tree.item(iid, open=YES)
                iid = self._findTreeIndexByPath(result.getPath())
                if iid:
                    self.tree.selection_set(iid)
    
    def _actionNewEntry(self):
        self.verifygroup = self.content.data.findGroup(self.treeselection[0])
        popup = PopupDialog(self.master, "New Entry", validate=self._validateEntry)
        if popup.result:
            entry = self.verifygroup.addEntry(popup.result)
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
            group = self.content.data.findGroup(self.treeselection[0])
            self.verifygroup = group.parent
            popup = PopupDialog(self.master, 'Rename Group', inittext=group.id, validate=self._validateGroup)
            if popup.result:
                openstate = self.tree.item(self.tree.selection())['open']
                group.id = popup.result
                group.parent.sortGroup()
                self.content.contentMutated()
                iid = self._findTreeIndexByPath(group.getPath())
                if iid:
                    self.tree.selection_set(iid)
                    self.tree.item(iid, open=openstate)
        elif renametype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            self.verifygroup = entry.parent
            popup = PopupDialog(self.master, 'Rename Entry', inittext=entry.id, validate=self._validateEntry)
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
            group = self.content.data.findGroup(self.treeselection[0])
            countchildren = group.countChildren() + 1
            countentries = group.countEntries()
            countpages = group.countPages()
            message = 'Are you sure you want to delete \"' + group.id + '\"?\n\n'
            message += str(countchildren) + ' group(s) will be deleted containing '
            message += str(countentries) + ' entries and '
            message += str(countpages) + ' page(s).'
            if messagebox.askyesno(
                'Delete Group?', 
                message,
                default=messagebox.NO
            ):
                group.parent.children.remove(group)
        elif deletetype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            if messagebox.askyesno(
                'Delete Entry?',
                'Are you sure you want to delete \"' + entry.id + '\"?\n\n' + str(len(entry.getPages())) + ' page(s) will be deleted.',
                default=messagebox.NO
            ):
                if self.content.editEntry == entry:
                    self.content.editEntry = None
                entry.parent.entries.remove(entry)
        self.content.contentMutated()
    
    def _actionDuplicate(self):
        duplicatetype = self.treeselection[3]
        if duplicatetype == 'group':
            group = self.content.data.findGroup(self.treeselection[0])
            self.verifygroup = group.parent
            group.parent.addGroup(self._incrementName(group.id, self._validateGroup))
        elif duplicatetype == 'entry':
            entry = self.content.data.findEntry(self.treeselection[0])
            self.verifygroup = entry.parent
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
                newparent = self.content.data.findGroup(self._getItemPathByTreeId(self.tree.selection()))
                movetype = self.treeselection[3]
                if movetype == 'group':
                    moveitem = self.content.data.findGroup(self.treeselection[0])
                    moveitem.parent.children.remove(moveitem)
                    moveitem.parent = newparent
                    newparent.children.append(moveitem)
                    newparent.sortGroups()
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
            self.verifygroup = self.content.data.findGroup(movepath)
            currentpath = self.content.getItemPathByString(self.treeselection[0])
            # First check what type of move we're doing
            movetype = self.treeselection[3]
            if movetype == 'group':
                group = self.content.data.findGroup(self.treeselection[0])
                # We can't drag a group inside itself, so welook up the verify group's parents
                parent = self.verifygroup.parent
                while parent != None:
                    if parent == group:
                        self.tree.selection_set()
                        return
                    parent = parent.parent
                # Check for name duplication in parent
                if self._validateGroup(group.id) is not ValidateResult.SUCCESS:
                    self.tree.selection_set()
                    return
                # Group move
                parentpath = group.parent.getPath()
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
    
    def _findTreeIndexByPath(self, path, treegroup=None):
        children = self.tree.get_children(treegroup)
        for child in children:
            if self._getItemValuesByTreeId(child)[0] == path:
                return child
            childres = self._findTreeIndexByPath(path, child)
            if childres:
                return childres
        return None

    def _cacheOpenState(self, treegroup, openstate):
        children = self.tree.get_children(treegroup)
        for child in children:
            self._cacheOpenState(child, openstate)
            item = self.tree.item(child)
            if item['open']:
                openstate.append(item['values'][0])

    def _applyOpenState(self, treegroup, openstate):
        children = self.tree.get_children(treegroup)
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

    def _populateTree(self, group:Group, tree):
        grouptype = 'group'
        if group.parent == None:
            grouptype = 'root'
        treegroup = self.tree.insert(tree, END, text=group.id, values=[group.getPath(), '', '', grouptype])
        # Show Entries
        for entry in group.entries:
            self.tree.insert(treegroup, END, text=entry.id, values=[entry.getPath(), entry.entrytype.value, len(entry.getPages()), 'entry'])
        # Show children
        for child in group.children:
            self._populateTree(child, treegroup)
        # Show empty if there are no children or entries in a group
        if len(group.entries) < 1 and len(group.children) < 1:
            self.tree.insert(treegroup, 0, text='[Empty]', values=[group.getPath(), '', '', 'empty'])
    
    def refreshView(self):
        self._populateTreeRoot()
        self._setupButtons(self.tree.selection())
