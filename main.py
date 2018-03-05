from data.DialogueContent import DialogueContent
from views.DialogueTree import DialogueTree
from views.EntryPanel import EntryPanel
from tkinter import Menu, Tk

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
        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        self._setupMenuBar(master)

        self.content = DialogueContent()
        self.content.mutateEvent.append(self.refreshViews)
        self.treeview = DialogueTree(master,self.content)
        self.editpanel = EntryPanel(master,self.content)

        self.refreshViews()

    def _setupMenuBar(self, master):
        menubar = Menu(master)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo")
        editmenu.add_command(label="Redo")
        menubar.add_cascade(label="Edit", menu=editmenu)

        master.config(menu=menubar)

    def refreshViews(self):
        self.treeview.refreshView()
        self.editpanel._populateEntryEditing()


root = Tk()
app = DialogueEditor(root)
root.mainloop()