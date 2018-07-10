import os
import xml.etree.ElementTree
from tkinter import *
from DialogueData import *
from DialogueData import Entry as DialogueEntry
from Content import Content
from PanelTree import PanelTree
from PanelText import PanelText
from TopRowMenu import TopRowMenu
from tkinter import filedialog, messagebox
from FileWriter import FileWriter
import PanelDetails
# TODO make this mac / pc compatible
import ctypes
from ctypes import wintypes, windll

# TODO change project name

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
        filemenu.add_command(label='New Project', command=self.projectNew)
        filemenu.add_command(label='Open Project', command=self.projectOpen, accelerator='Ctrl+O')
        filemenu.add_command(label='Save Project', command=self.projectSave, accelerator='Ctrl+S')
        filemenu.add_command(label='Save Project As', command=self.projectSaveAs)
        filemenu.add_separator()
        filemenu.add_command(label='Import XML', command=self.importFile)
        filemenu.add_command(label='Export XML', command=self.exportFile)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=master.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label='Undo', command=self.undo, accelerator='Ctrl+Z')
        editmenu.add_command(label='Redo', command=self.redo, accelerator='Ctrl+R')
        editmenu.add_separator()
        editmenu.add_command(label='Delete Region', command=self.deleteRegion)
        menubar.add_cascade(label='Edit', menu=editmenu)

        master.config(menu=menubar)

        master.bind_all('<Control-Key-o>', self.projectOpen)
        master.bind_all('<Control-Key-s>', self.projectSave)
        master.bind_all('<Control-Key-z>', self.undo)
        master.bind_all('<Control-Key-r>', self.redo)

    def refreshViews(self):
        self.paneltree.refreshView()
        self.paneltext.refreshView()
        self.paneldetails.refreshView()
        self.toprow.refreshView()
    
    def undo(self, *args):
        undocontent = Content.getUndoContent()
        if undocontent:
            self.parseXmlProject(undocontent)
            self.refreshViews()
    
    def redo(self, *args):
        redocontent = Content.getRedoContent()
        if redocontent:
            self.parseXmlProject(redocontent)
            self.refreshViews()

    def _desktopPath(self):
        CSIDL_COMMON_DESKTOPDIRECTORY = 16
        _SHGetFolderPath = windll.shell32.SHGetFolderPathW
        _SHGetFolderPath.argtypes = [wintypes.HWND,
                                    ctypes.c_int,
                                    wintypes.HANDLE,
                                    wintypes.DWORD, wintypes.LPCWSTR]
        path_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        result = _SHGetFolderPath(0, CSIDL_COMMON_DESKTOPDIRECTORY, 0, 0, path_buf)
        return path_buf.value
    
    def projectNew(self):
        if messagebox.askokcancel(title='New Project?', message='You will lose any unsaved data.', default=messagebox.CANCEL):
            Content.initData()
            self.refreshViews()
    
    def projectOpen(self, *args):
        pathload = filedialog.askopenfilename(title='Open Project', filetypes=[('dpr files', '*.dpr')])        
        if pathload:
            Content.projectPath = pathload
            file = open(pathload, 'r')
            if file:
                load = file.read()
                self.parseXmlProject(load)
                Content.data.clearModified()
            else:
                return
                # TODO LOG
    
    def projectSave(self, *args):
        if Content.projectPath == '':
            self._projectSave(None)
            return
        self._projectSave(Content.projectPath)
    
    def projectSaveAs(self):
        self._projectSave(None)

    def _projectSave(self, path):
        pathsave = path
        if pathsave == None:
            pathsave = filedialog.asksaveasfilename(title='Save Project As', filetypes=[('dpr files', '*.dpr')], initialfile='project.dpr')
        if pathsave:
            Content.projectPath = pathsave
            file = open(pathsave, 'w')
            if file:
                Content.data.clearModified()
                file.write(Content.data.serialize())
                file.close()
                self.refreshViews()

    def exportFile(self):
        pathsave = self._desktopPath() + '\\translation.xml'
        if pathsave:
            file = open(pathsave, 'w')
            if file:
                allentries = Content.data.allEntries()
                self.writer.clear()
                self.writer.initXml()
                self.writer.writeLine(0, ["<data>"])
                for regionname in Content.allregions:
                    self.writer.writeLine(1, ["<region id=\"", regionname, "\">"])
                    for entry in allentries:
                        region = entry.getRegion(regionname)
                        self.writer.writeLine(2, [
                            "<line id=\"", 
                            region.parent.getPath(), 
                            "\" flag=\"", 
                            region.parent.getExportFlag(), 
                            "\"><![CDATA[", 
                            region.combinedPages(),
                            "]]></line>"
                        ])
                    self.writer.writeLine(1, ["</region>"])
                self.writer.writeLine(0, ["</data>"])
                
                file.write(self.writer.getContent())
                file.close()

    def importFile(self):
        pathload = filedialog.askopenfilename(title='Import XML', filetypes=[("xml files","*.xml")])
        if pathload:
            self.parseXmlImport(pathload)
    
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

    def parseXmlImport(self, path):
        root = xml.etree.ElementTree.parse(path).getroot()
        if root.tag == 'data':
            Content.clearRegions()
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
            Content.markRestorePoint()
            Content.contentMutated()
        
    def parseXmlProject(self, content):
        # This comes in as a pre-parsed string since it can be from memory
        # This doesn't change the modified flags, since it can be undone / redone
        root = xml.etree.ElementTree.fromstring(content)
        Content.clearRegions()
        editpath = ''
        if Content.editEntry != None:
            editpath = Content.editEntry.getPath()
        # Top level parsing
        for n in root:
            if n.tag == 'info':
                self._parseInfoNode(n)
            elif n.tag == 'group':
                Content.data = self._parseGroupNode(n, None)
            else:
                print(n.tag)
        Content.checkEditPath(editpath)
        Content.data.sortEntries()
        Content.contentMutated()        
    
    def _parseInfoNode(self, node):
        for n in node:
            if n.tag == 'activeregion':
                Content.region = n.text
            elif n.tag == 'version':
                pass # TODO version checking
            elif n.tag == 'name':
                Content.projectName = n.text
            elif n.tag == 'regions':
                for r in n:
                    Content.allregions.append(r.text)
            else:
                print('Info: ' + n.tag)
    
    def _parseGroupNode(self, node, parent):
        group = Group(node.attrib['id'], parent)
        group.modified = node.attrib['mod'] == 't'
        for n in node:
            if n.tag == 'group':
                group.children.append(self._parseGroupNode(n, group))
            elif n.tag == 'entry':
                self._parseEntryNode(n, group)
            else:
                print('group: ' + n.tag)
        group.sortGroups()
        group.sortEntries()
        return group
    
    def _parseEntryNode(self, node, parent):
        entry = DialogueEntry(node.attrib['id'], EntryType[node.attrib['type']], parent)
        entry.entrycolor = EntryColors[node.attrib['color']]
        entry.modified = node.attrib['mod'] == 't'
        parent.entries.append(entry)
        for n in node:
            if n.tag == 'region':
                self._parseRegionNode(n, entry)
            else:
                print('entry: ' + n.tag)
    
    def _parseRegionNode(self, node, parent):
        region = parent.getRegion(node.attrib['id'])
        if region.id not in Content.allregions:
            Content.allregions.append(region.id)
        region.clearPages()
        allpages = []
        for n in node:
            processedText = n.text
            processedText = processedText.replace('\\n', '\n')
            processedText = processedText.replace('\\t', '\t')
            allpages.append((int(n.attrib['index']),processedText))
        # Sort the pages to be sure we're in the right order
        allpages.sort(key=lambda tup: tup[0])
        for p in allpages:
            page = region.addPage()
            text = p[1]
            if text == None:
                text = ''
            page.content = text

root = Tk()
app = DialogueEditor(root)
root.mainloop()