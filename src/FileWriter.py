class FileWriter:
    def __init__(self):
        self._val = ''
    
    def writeLine(self, indent, line):
        for i in range(0,indent):
            self._val += '\t'
        self._val += line + '\n'
    
    def clear(self):
        self._val = ''
    
    def getContent(self):
        return self._val
