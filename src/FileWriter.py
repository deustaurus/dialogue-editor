class FileWriter:
    def __init__(self):
        self._val = []
    
    def writeLine(self, indent, line):
        for i in range(0,indent):
            self._val.append('\t')
        for l in line:
            self._val.append(l)
        self._val.append('\n')
    
    def clear(self):
        self._val = []
    
    def initXml(self):        
        self.writeLine(0, ["<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n"])

    def getContent(self):
        return ''.join(self._val)
