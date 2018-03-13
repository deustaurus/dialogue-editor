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
    redolist = []

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
        Content.editEntry = None
        Content.markRestorePoint()

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
        # We marked a new point, redo list destroyed
        Content.redolist = []
        # Save the current data
        Content.undolist.append(Content.data.serialize())
        # Cap the list
        while len(Content.undolist) > Content.maxundo:
            Content.undolist.pop(0)

    @staticmethod
    def getUndoContent():
        # If there's nothing to undo to, return None
        # The last undo index is always the current one, so we can't return that
        if len(Content.undolist) < 2:
            return None
        # Put the current state in the redo list
        Content.redolist.insert(0, Content.undolist.pop())
        # Return the last bit of the undo list to switch to
        return Content.undolist[-1]
    
    @staticmethod
    def getRedoContent():
        # If there's nothing to redo to, return none
        if len(Content.redolist) < 1:
            return None
        # Put our current state back in the undo list
        Content.undolist.append(Content.redolist.pop(0))
        # Return the first bit of the redo list
        return Content.undolist[-1]
