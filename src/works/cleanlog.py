import glob
import sqlite3
import re
import ConfigParser
from datetime import datetime as dt
from datetime import date

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('../log.db')
        self.cursor = self.connection.cursor()
    def insert(self,log):
        query="INSERT OR IGNORE INTO log (systemId,timeStamp,type,typeError,line,message,path,lineNumber) VALUES(?,?,?,?,?,?,?,?)"
        self.cursor.execute(query,log.printLog())
        self.connection.commit()
class logRecord:
    def __init__(self):
        self.type=''
        self.system=''
        self.typeError=''
        self.line=''
        self.timeStamp=''
        self.parse=[]
        self.path=''
        self.lineNumber=''
        self.message=''
        self.year='1900'
        self.month='12'
        self.day='31'
        self.hour='24'
        self.minute='59'
        self.second='59'
    def setSystem(self,system):
        self.system=system
    def printLog(self):
        return [self.system,self.timeStamp,self.type,self.typeError,self.line,self.message,self.path,self.lineNumber]
    def setPath(self):
        path = re.search('in (/.*?\s)', self.parse[-1])
        self.path=path.group(1) if path else ''
    def setlineNumber(self):
        lineNumber= re.search('line (.*)(?<=\D)(\d+)', self.parse[-1])
        self.lineNumber=lineNumber.group(2) if lineNumber else ''
    def setTimestamp(self,timeStamp):
        self.year,self.month,self.day,
        self.timeStamp=timeStamp
    def setLine(self,line):
        self.line=line
    def setParse(self,parse):
        self.parse=parse

    def isLog(self):
        self.type=self.parse[0]
        if len(self.parse)>0:
            self.typeError=self.parse[1]
            self.message=":".join(self.parse[1:])
          
        
    def isDebug(self):
        self.type=self.parse[0]
        self.message=":".join(self.parse[1:])
        
class cleanlog():
    def __init__(self,path,daysToProccess):
        self.filesPath=path
        self.typeOfLogs=['system','exception']
        self.blankpatterns=re.compile(r'^\s|^\(|^\)|^}|^{')
        self.database=Database()
        self.daysToProccess=daysToProccess
    def analysisSystem(self,fileName):
        index=0
        multiline=[]
        currentLine=''
        for line in reversed(open(fileName)).readlines():
            index+=1
#             print index
            previusLine=currentLine           
            currentLine=line
                        
            if self.blankpatterns.search(currentLine):
                multiline.append(previusLine)
                continue
            else:
                if len(multiline)>1:
                    multilineString=self.getMultiline(multiline)
                    previusLine=multilineString
                multiline=[]        
            if len(previusLine)<=2:
                continue
            log=logRecord()
            log.setSystem("1")
            log.setTimestamp(previusLine[:26].strip())
            print log.setTimestamp
            parse= previusLine[26:].split(":")
            log.setLine(previusLine)
            log.setParse(parse)
            log.setPath()
            log.setlineNumber()
            if "DEBUG" in previusLine:
                log.isDebug()
            else:
                log.isLog()
            self.database.insert(log) 
        print index
            
    def analysisException(self,fileName):
        pass
    def getMultiline(self,multiline):
        multilineString=''
        for line in multiline:
            multilineString+=line
        return multilineString    
    def run(self):
#         for typeOfLog in self.typeOfLogs:
#             print typeOfLog
#             for fileName in glob.glob(self.filesPath+typeOfLog+'*.*'):
#                 print fileName
        fileName='/Users/carlos/Downloads/tmp/system.log'
        self.analysisSystem(fileName)
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    path = config.get('config', "path")
    daysToProccess = config.get('config', "daysToProccess")
    today = date.today()
    print today
       
    cleaner = cleanlog(path,daysToProccess)
    cleaner.run()
            
            