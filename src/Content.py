import re
import string
import DialogueData

class Content:

    # Static
    region = 'en'
    mutateEvent = []
    allregions = ['en']
    editEntry = None

    # Content root
    data = None

    # def __init__(self):
    #     # Editing Content
    #     self.editEntry = None

    #     self.mutateEvent = []
    #     self.allregions = ['en']

    #     # Content root
    #     self.data = DialogueData.Group('Content')

    @staticmethod
    def initData():
        Content.data = DialogueData.Group('Content')
        Content.data.clearModified()

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
