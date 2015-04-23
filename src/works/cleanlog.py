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
        pass
    def analysisSystem(self,fileName):
        index=0
        notice={}
        for line in open(fileName).xreadlines():
            index+=1
#             print index           
            if line=="":
                continue
            log=logSystemRecord()
            log.setTimestamp(line[:26].strip())
            parse= line[26:].split(":")
            log.setLine(line)
            log.setParse(parse)
            log.setPath()
            log.setlineNumber()
            if "Notice:" in line:
                log.isNotice()
                continue
            if "Warning:" in line:
                continue
            if "Recoverable Error:" in line:
                continue
            if "failed to open stream:" in line:
                continue
            if "include():" in line:
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
                print line
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
            
            