import os
import string
import re

from tkinter import *
from tkinter import ttk, messagebox
from data.DialogueData import *
from views.SimpleDialog import Dialog
from views.DialogueTree import DialogueTree
from views.EntryEditPanel import EntryEditPanel

# TODO Text input validation
# TODO make buttons for the right click menu stuff
# TODO some nice bg colors and stuff for list
# TODO bg color for currently edited entry and parents
# TODO load from xml
# TODO save to xml
# TODO undo tree?

class DialogueEditor:

    def __init__(self, master):
        self.master = master
        master.title("Dialogue Editor")
        master.geometry("800x600")

        self.tree = DialogueTree(master,self)
        self.editpanel = EntryEditPanel(master,self)

        self.editEntry = None
        self.nodemodify = None
        self.entrymodify = None

        self._setupMenuBar(master)

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

        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

        self._refreshViews()

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
        self.nodemodify = self.content.findNode(self.tree.treeSelection[0])
        popup = Dialog(self.master, "New Group", validate=self._validateNewGroupName)
        if popup.result:
            result = self.nodemodify.addNode(popup.result)
            self._refreshViews()
            iid = self.tree._findTreeIndexByPath(result.parent.getPath())
            if iid:
                self.tree.tree.item(iid, open=YES)
                iid = self.tree._findTreeIndexByPath(result.getPath())
                if iid:
                    self.tree.tree.selection_set(iid)
    
    def _newEntryAction(self):
        self.nodemodify = self.content.findNode(self.tree.treeSelection[0])
        popup = Dialog(self.master, "New Entry", validate=self._validateNewEntryName)
        if popup.result:
            entry = self.nodemodify.addEntry(popup.result)
            self.editEntry = entry
            self._refreshViews()
            iid = self.tree._findTreeIndexByPath(entry.parent.getPath())
            if iid:
                self.tree.tree.item(iid, open=YES)
                iid = self.tree._findTreeIndexByPath(entry.getPath())
                if iid:
                    self.tree.tree.selection_set(iid)
    
    def _renameObjectAction(self):
        renametype = self.tree.treeSelection[3]
        if renametype == 'group':
            self.nodemodify = self.content.findNode(self.tree.treeSelection[0])
            popup = Dialog(self.master, 'Rename Group', inittext=self.nodemodify.id, validate=self._validateRenameGroup)
            if popup.result:
                openstate = self.tree.tree.item(self.tree.tree.selection())['open']
                self.nodemodify.id = popup.result
                self.nodemodify.parent.sortNodes()
                self._refreshViews()
                iid = self.tree._findTreeIndexByPath(self.nodemodify.getPath())
                if iid:
                    self.tree.tree.selection_set(iid)
                    self.tree.tree.item(iid, open=openstate)
        elif renametype == 'entry':
            self.entrymodify = self.content.findEntry(self.tree.treeSelection[0])
            popup = Dialog(self.master, 'Rename Entry', inittext=self.entrymodify.id, validate=self._validateRenameEntry)
            if popup.result:
                self.entrymodify.id = popup.result
                self.entrymodify.parent.sortEntries()
                self._refreshViews()
                iid = self.tree._findTreeIndexByPath(self.entrymodify.getPath())
                if iid:
                    self.tree.tree.selection_set(iid)

    def _deleteObjectAction(self):
        deletetype = self.tree.treeSelection[3]
        if deletetype == 'group':
            node = self.content.findNode(self.tree.treeSelection[0])
            # TODO Warn about how many children we're deleting?
            if messagebox.askyesno(
                'Delete Node?', 
                'Are you sure you want to delete \"' + node.id + '\"?', 
                default=messagebox.NO
            ):
                node.parent.children.remove(node)
        elif deletetype == 'entry':
            entry = self.content.findEntry(self.tree.treeSelection[0])
            # TODO Warn about how many pages we're deleting
            if messagebox.askyesno(
                'Delete Entry?',
                'Are you sure you want to delete \"' + entry.id + '\"?',
                default=messagebox.NO
            ):
                entry.parent.entries.remove(entry)
        self._refreshViews()
    
    def _duplicateIdAction(self):
        duplicatetype = self.tree.treeSelection[3]
        if duplicatetype == 'group':
            self.nodemodify = self.content.findNode(self.tree.treeSelection[0])
            self.nodemodify.parent.addNode(self._incrementName(self.nodemodify.id, self._validateRenameGroup))
        elif duplicatetype == 'entry':
            self.entrymodify = self.content.findEntry(self.tree.treeSelection[0])
            self.entrymodify.parent.addEntry(self._incrementName(self.entrymodify.id, self._validateRenameEntry))
        self._refreshViews()

    def _refreshViews(self):
        self.tree._populateTreeRoot()
        self.editpanel._populateEntryEditing()

    def _getItemPathByString(self, string):
        return self.content.findNode(string).getPath()

root = Tk()
app = DialogueEditor(root)
root.mainloop()