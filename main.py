import os
import xml.etree.ElementTree
from data.DialogueData import *
from data.DialogueContent import DialogueContent
from views.DialogueTree import DialogueTree
from views.EntryPanel import EntryPanel
from tkinter import Menu, Tk, filedialog

# TODO import from xml
# TODO export to xml
# TODO language modes?
# TODO project file, too for open / save

class DialogueEditor:
    def __init__(self, master):
        self.master = master

        master.title("Dialogue Editor")
        master.geometry("800x600")
        self._setupMenuBar(master)

        self.content = DialogueContent()
        self.content.mutateEvent.append(self.refreshViews)
        self.treeview = DialogueTree(master,self.content)
        self.entrypanel = EntryPanel(master,self.content)
        
        master.rowconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

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
        # TODO lots of logging and safety here
        pathdesktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        pathload = filedialog.askopenfilename(initialdir=pathdesktop, title='Open File', filetypes=[("xml files","*.xml")])
        if pathload:
            self.parseFile(pathload)

    def parseFile(self, path):        
        root = xml.etree.ElementTree.parse(path).getroot()
        if root.tag == 'data':
            self.content.data.children = []
            for regionnode in root:
                if regionnode.tag == 'region':
                    region = regionnode.attrib['id']
                    print(region)
                    for linenode in regionnode:
                        lineid = linenode.attrib['id']
                        lineflag = linenode.attrib['flag']
                        entry = self.content.data.addEntryPath(lineid)
                        if lineflag == 'r':
                            entry.entrytype = EntryType.DIARY
                        linetext = linenode.text.split('%r')
                        for line in linetext:
                            line = line.replace('\\n', '\n')
                            page = entry.addPage()
                            page.content = line
                        entry.editPage = 0
            self.content.contentMutated()

root = Tk()
app = DialogueEditor(root)
root.mainloop()