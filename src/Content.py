import re
import string
import DialogueData

class Content:

    # Static
    region = 'en'
    mutateEvent = []
    allregions = ['en']
    editEntry = None
    projectName = 'translation'
    projectPath = ''
    undolist = []
    undoindex = 0

    maxundo = 50

    # Content root
    data = None

    @staticmethod
    def checkEditPath(path):        
        if path != '':
            Content.editEntry = Content.data.findEntry(path)
        else:
            Content.editEntry = None

    @staticmethod
    def initData():
        Content.projectName = 'translation'
        Content.projectPath = ''
        Content.data = DialogueData.Group('Content')
        Content.data.clearModified()
        editEntry = None

    @staticmethod
    def contentMutated():
        for func in Content.mutateEvent:
            func()

    @staticmethod
    def getItemPathByString(string):
        return Content.data.findGroup(string).getPath()
    
    @staticmethod
    def clearRegions():
        Content.allregions = []

    @staticmethod
    def deleteRegion(regionid):
        Content.allregions.remove(regionid)
        Content.region = Content.allregions[0]
        Content.data.deleteRegion(regionid)

    @staticmethod
    def markRestorePoint():
        # If we've backed down the undo tree, and we're saving a new one, we need to prune from here forward
        while len(Content.undolist) > Content.undoindex + 1:
            Content.undolist.pop()
        # Save the current data
        Content.undolist.append(Content.data.serialize())
        # Cap the list
        while len(Content.undolist) > Content.maxundo:
            Content.undolist.pop(0)
        # Set the new index
        Content.undoindex = len(Content.undolist) - 1
