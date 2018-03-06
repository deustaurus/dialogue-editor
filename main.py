import os
import xml.etree.ElementTree
from data.DialogueContent import DialogueContent
from views.DialogueTree import DialogueTree
from views.EntryPanel import EntryPanel
from tkinter import Menu, Tk, filedialog

# TODO load from xml
# TODO save to xml
# TODO language modes?

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
        self.entrypanel = EntryPanel(master,self.content)

        self.refreshViews()

    def _setupMenuBar(self, master):
        menubar = Menu(master)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile)
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
        self.entrypanel.refreshView()
    
    def openFile(self):
        pathdesktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        pathload = filedialog.askopenfilename(initialdir=pathdesktop, title='Open File', filetypes=[("xml files","*.xml")])
        if pathload:
            print(pathload)
            e = xml.etree.ElementTree.parse(pathload).getroot()
        else:
            print('No file to load')

root = Tk()
app = DialogueEditor(root)
root.mainloop()