import re
import string
import DialogueData

class Content:

    # Static
    region = 'en'

    def __init__(self):
        # Editing Content
        self.editEntry = None

        self.mutateEvent = []
        self.allregions = ['en']

        # Content root
        self.data = DialogueData.Group('Content')

    def contentMutated(self):
        for func in self.mutateEvent:
            func()

    def getItemPathByString(self, string):
        return self.data.findGroup(string).getPath()
    
    def clearRegions(self):
        self.allregions = []

    def deleteRegion(self, regionid):
        self.allregions.remove(regionid)
        Content.region = self.allregions[0]
        self.data.deleteRegion(regionid)
