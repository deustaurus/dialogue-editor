import os
import xml.etree.ElementTree
from tkinter import *
from DialogueData import *
from Content import Content
from PanelTree import PanelTree
from PanelText import PanelText
from TopRowMenu import TopRowMenu
from tkinter import filedialog, messagebox
import PanelDetails

# TODO project file, too for open / save
# TODO export to xml

class DialogueEditor:
    def __init__(self, master):
        self.master = master

        master.title("Dialogue Editor")
        master.geometry("1024x768")
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        self._setupMenuBar(master)

        self.content = Content()
        self.content.mutateEvent.append(self.refreshViews)

        topRowFrame = Frame(master, padx=5, pady=5)
        topRowFrame.grid(row=0, column=0, sticky=NSEW)
        self.toprow = TopRowMenu(topRowFrame, self.content)

        mainFrame = Frame(master)
        mainFrame.grid(row=1, column=0, sticky=NSEW)

        self.paneltree = PanelTree(mainFrame,self.content)
        self.paneltext = PanelText(mainFrame,self.content)
        self.paneldetails = PanelDetails.PanelDetails(mainFrame, self.content)
        
        mainFrame.rowconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=1)

        self.refreshViews()

    def _setupMenuBar(self, master):
        menubar = Menu(master)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open Project')
        filemenu.add_command(label='Save Project')
        filemenu.add_separator()
        filemenu.add_command(label='Import XML', command=self.openFile)
        filemenu.add_command(label='Export XML')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=master.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo')
        editmenu.add_command(label='Redo')
        editmenu.add_separator()
        editmenu.add_command(label='Delete Region', command=self.deleteRegion)
        menubar.add_cascade(label='Edit', menu=editmenu)

        master.config(menu=menubar)

    def refreshViews(self):
        self.paneltree.refreshView()
        self.paneltext.refreshView()
        self.paneldetails.refreshView()
        self.toprow.refreshView()
    
    def openFile(self):
        # TODO lots of logging and safety here
        pathdesktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        pathload = filedialog.askopenfilename(initialdir=pathdesktop, title='Import XML', filetypes=[("xml files","*.xml")])
        if pathload:
            self.parseFile(pathload)
    
    def deleteRegion(self):
        if len(self.content.allregions) < 2:
            messagebox.showwarning(title='Delete Region', message='Can\'t delete the last region.')
            return
        if messagebox.askyesno(
            'Delete Region?', 
            'Are you sure you want to delete the region named \'' + Content.region + '\'?',
            default=messagebox.NO
        ):
            self.content.deleteRegion(Content.region)
            self.refreshViews()

    def parseFile(self, path):        
        root = xml.etree.ElementTree.parse(path).getroot()
        self.content.clearRegions()
        if root.tag == 'data':
            self.content.data.children = []
            for regionnode in root:
                if regionnode.tag == 'region':
                    regionname = regionnode.attrib['id']
                    self.content.allregions.append(regionname)
                    for linenode in regionnode:
                        lineid = linenode.attrib['id']
                        lineflag = linenode.attrib['flag']
                        entry = self.content.data.addEntryPath(lineid)
                        if lineflag == 'r':
                            entry.entrytype = EntryType.DIARY
                        region = entry.getRegion(regionname)
                        region.clearPages()
                        linetext = linenode.text.split('%r')
                        # Delete dummy page from the created group
                        for line in linetext:
                            line = line.replace('\\n', '\n')
                            page = region.addPage()
                            page.content = line
            if Content.region not in self.content.allregions:
                print('reset region')
                Content.region = self.content.allregions[0]
            self.content.editEntry = None
            self.content.contentMutated()

root = Tk()
app = DialogueEditor(root)
root.mainloop()