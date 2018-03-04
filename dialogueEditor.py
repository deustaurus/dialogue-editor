import os

from tkinter import *
from tkinter import ttk
from Data import *

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
        self.content.addNode('Bome')        

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

        self.popupmenu.add_command(label='New Group')
        self.popupmenu.add_command(label='New Entry')
        self.popupmenu.add_command(label='Delete')

    def _createTree(self, master):
        self.dataCols = ('group', 'type', 'pages')
        self.tree = ttk.Treeview(columns=self.dataCols, displaycolumns=['type','pages'])
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

    def _populateTreeRoot(self):
        self.tree.delete(*self.tree.get_children())
        self._populateTree(self.content, '')

    def _populateTree(self, node, tree):
        nodetype = 'group'
        if node.parent == None:
            nodetype = 'root'
        treenode = self.tree.insert(tree, END, text=node.id, values=[node.getPath(), '', '', nodetype])
        for child in node.children:
            self._populateTree(child, treenode)
        if len(node.entries) > 0:
            for entry in node.entries:
                self.tree.insert(treenode, END, text=entry.id, values=[entry.getPath(), entry.entrytype.value, len(entry.pages), 'entry'])
        else:
            if node.parent != None:
                self.tree.insert(treenode, END, text='[Empty]', values=[node.getPath(), '', '', 'empty'])

    def _rightClickTree(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                # Default settings, group mode
                self.selectiontype = 'group'
                self.popupmenu.entryconfig(0, state=ACTIVE)
                self.popupmenu.entryconfig(1, state=ACTIVE)
                self.popupmenu.entryconfig(2, state=ACTIVE)
                # Get information
                self.tree.selection_set(iid)
                self.selection = self.tree.item(iid)['values'][2]
                print(self.tree.item(iid)['values'])
                # Check information
                if self.selection == 'root':
                    # Root content can't be deleted, or have entries added
                    self.popupmenu.entryconfig(1, state=DISABLED)
                    self.popupmenu.entryconfig(2, state=DISABLED)
                elif self.selection == 'entry':
                    # An entry can have anything added to it
                    self.selectiontype = 'entry'
                elif self.selection == 'empty':
                    # You can't delete an empty object
                    self.popupmenu.entryconfig(2, state=DISABLED)                    

                self.popupmenu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.popupmenu.grab_release()
        else:
            self.tree.selection_set()

root = Tk()
app = DialogueEditor(root)
root.mainloop()