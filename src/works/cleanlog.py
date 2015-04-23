import glob
import sqlite3
import re
class logSystemRecord:
    def __init__(self):
        self.type=''
        self.line=''
        self.timestamp=''
        self.parse=[]
        self.path=''
        self.line=''
        self.lineNumber=''

    def insert(self):
        pass
    def setPath(self):
        path = re.search('in (/.*?\s)', self.parse[-1])
        self.path=path.group(0) if path else ''
    def setlineNumber(self):
        lineNumber= re.search('line (.*)(?<=\D)(\d+)', self.parse[-1])
        self.lineNumber=lineNumber.group(2) if lineNumber else ''
    def setTimestamp(self,timestamp):
        self.timestamp=timestamp
    def setLine(self,line):
        self.line=line
    def setParse(self,parse):
        self.parse=parse
        
    def isNotice(self):
        if len(self.parse)==7:
            print  self.parse
        
class cleanlog():
    def __init__(self):
        self.filesPath='/Users/carlos/Downloads/tmp/'
        self.typeOfLogs=['system','exception']
        self.blankpatterns=re.compile(r'^\s|^\(|^\)|^}|^{')
        pass
    def analysisSystem(self,fileName):
        index=0
        notice={}
        multiline=[]
        multilineString=''
        currentLine=''
        for line in open(fileName).xreadlines():
            index+=1
            previusLine=currentLine           
            currentLine=line
                        
            if self.blankpatterns.search(currentLine):
                multiline.append(previusLine)
                continue
            else:
                if len(multiline)>1:
                    print "***********" +str(index)
                    multilineString=''
                    for line in multiline:
                        multilineString+=line
                    print multilineString
                multiline=[]
                
#             print index           
            if previusLine=="":
                continue
            log=logSystemRecord()
            log.setTimestamp(previusLine[:26].strip())
            parse= previusLine[26:].split(":")
            log.setLine(previusLine)
            log.setParse(parse)
            log.setPath()
            log.setlineNumber()
            if "Notice:" in previusLine:
                log.isNotice()
                continue
            if "Warning:" in previusLine:
                continue
            if "Recoverable Error:" in previusLine:
                continue
            if "failed to open stream:" in previusLine:
                continue
            if "include():" in previusLine:
                continue
            
            if len(parse)==2:
                continue
            if len(parse)==0:
                continue            
            if len(parse)==1:
                continue
            if len(parse)!=3:
                
                print index
                print len(parse)
                print previusLine
                for part in parse:
                    print part.strip()
                return
            
        print index
        for key in notice:
            print key
            print "count "+ str(len(notice[key]))
            
    def analysisException(self,fileName):
        pass
    def run(self):
#         for typeOfLog in self.typeOfLogs:
#             print typeOfLog
#             for fileName in glob.glob(self.filesPath+typeOfLog+'*.*'):
#                 print fileName
        fileName='/Users/carlos/Downloads/tmp/system.log.web03'
        self.analysisSystem(fileName)
if __name__ == "__main__":
    cleaner = cleanlog()
    cleaner.run()
            
            