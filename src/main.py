import os
import xml.etree.ElementTree
from tkinter import *
from DialogueData import *
from Content import Content
from PanelTree import PanelTree
from PanelText import PanelText
from TopRowMenu import TopRowMenu
from tkinter import filedialog, messagebox
from FileWriter import FileWriter
import PanelDetails

# TODO project file, too for open / save
# TODO keyboard commands
# TODO undo tree?

class DialogueEditor:
    def __init__(self, master):
        self.master = master

        master.title("Dialogue Editor")
        master.geometry("1024x768")
        master.rowconfigure(1, weight=1)
        master.columnconfigure(1, weight=1)

        self._setupMenuBar(master)

        self.writer = FileWriter()

        Content.initData()
        Content.mutateEvent.append(self.refreshViews)

        self.toprow = TopRowMenu(master)
        self.paneltree = PanelTree(master)
        self.paneltext = PanelText(master)
        self.paneldetails = PanelDetails.PanelDetails(master)

        self.refreshViews()

    def _setupMenuBar(self, master):
        menubar = Menu(master)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open Project')
        filemenu.add_command(label='Save Project')
        filemenu.add_separator()
        filemenu.add_command(label='Import XML', command=self.importFile)
        filemenu.add_command(label='Export XML', command=self.exportFile)
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
    
    def exportFile(self):
        pathdesktop = os.path.join(os.environ['HOMEPATH'], 'Desktop')
        pathsave = filedialog.asksaveasfilename(initialdir=pathdesktop, title='Export XML', filetypes=[('xml fies', '*.xml')])
        if pathsave:
            file = open(pathsave, 'w')
            if file:
                allentries = Content.data.allEntries()
                self.writer.clear()
                self.writer.writeLine(0, "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n")
                self.writer.writeLine(0, "<data>")
                for regionname in Content.allregions:
                    self.writer.writeLine(1, "<region id=\"" + regionname + "\">")
                    for entry in allentries:
                        region = entry.getRegion(regionname)
                        self.writer.writeLine(2, "<line id=\"" + region.parent.getPath() + "\" flag=\"" + region.parent.getExportFlag() + "\"><![CDATA[" + region.combinedPages() + "]]></line>")
                    self.writer.writeLine(1, "</region>")
                self.writer.writeLine(0, "</data>")
                
                file.write(self.writer.getContent())
                file.close()

    def importFile(self):
        # TODO lots of logging and safety here
        pathdesktop = os.path.join(os.environ["HOMEPATH"], "Desktop")
        pathload = filedialog.askopenfilename(initialdir=pathdesktop, title='Import XML', filetypes=[("xml files","*.xml")])
        if pathload:
            self.parseXml(pathload)
    
    def deleteRegion(self):
        if len(Content.allregions) < 2:
            messagebox.showwarning(title='Delete Region', message='Can\'t delete the last region.')
            return
        if messagebox.askyesno(
            'Delete Region?', 
            'Are you sure you want to delete the region named \'' + Content.region + '\'?',
            default=messagebox.NO
        ):
            Content.deleteRegion(Content.region)
            self.refreshViews()

    def parseXml(self, path):        
        root = xml.etree.ElementTree.parse(path).getroot()
        Content.clearRegions()
        if root.tag == 'data':
            Content.data.children = []
            for regionnode in root:
                if regionnode.tag == 'region':
                    regionname = regionnode.attrib['id']
                    Content.allregions.append(regionname)
                    for linenode in regionnode:
                        lineid = linenode.attrib['id']
                        lineflag = linenode.attrib['flag']
                        entry = Content.data.addEntryPath(lineid)
                        if lineflag == 'r':
                            entry.entrytype = EntryType.DIARY
                        region = entry.getRegion(regionname)
                        # Ignore empty nodes
                        if linenode.text and len(linenode.text) > 0:
                            region.clearPages()
                            linetext = linenode.text.split('%r')
                            for line in linetext:
                                line = line.replace('\\n', '\n')
                                page = region.addPage()
                                page.content = line
            if Content.region not in Content.allregions:
                Content.region = Content.allregions[0]
            Content.editEntry = None
            Content.data.clearModified()
            Content.contentMutated()

root = Tk()
app = DialogueEditor(root)
root.mainloop()