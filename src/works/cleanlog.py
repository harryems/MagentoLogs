import glob
import sqlite3
import re
import ConfigParser
from datetime import datetime as dt
from datetime import timedelta
import time
import os

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('./log.db')
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
#         self.year='1900'
#         self.month='12'
#         self.day='31'
#         self.hour='24'
#         self.minute='59' 
#         self.second='59'
    def setSystem(self,system):
        self.system=system
    def printLog(self):
        return [unicode(self.system, 'utf-8'),unicode(self.timeStamp, 'utf-8'),unicode(self.type, 'utf-8'),unicode(self.typeError, 'utf-8'),unicode(self.line, 'utf-8'),unicode(self.message, 'utf-8'),unicode(self.path, 'utf-8'),unicode(self.lineNumber, 'utf-8')]
    def setPath(self,path):
#         path = re.search('in (/.*?\s)', self.parse[-1])
#         self.path=path.group(1) if path else ''
        self.path=path
    def setlineNumber(self,lineNumber):
#         lineNumber= re.search('line (.*)(?<=\D)(\d+)', self.parse[-1])
#         self.lineNumber=lineNumber.group(2) if lineNumber else ''
        self.lineNumber=lineNumber
    def setTimestamp(self,timeStamp):
#         print timeStamp
#         match=re.match('(\d{4})[\-](\d{1,2})[\-](\d{1,2}).(\d{1,2}).(\d{1,2}).(\d{1,2})',timeStamp)
#         if match:
#             self.year,self.month,self.day,self.hour,self.minute,self.second=list(match.groups())
        self.timeStamp=timeStamp
#         print self.timeStamp
    def setTypeError(self,typeError):
        self.typeError=typeError
    def setType(self,_type):
        self.type=_type
    def setMessage(self,message):
        self.message=message
    def getTimestamp(self):
        return self.timeStamp
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
    def analysisException(self,fileName):
        multiline=[]
        index=0        
        toDate=dt.today()- timedelta(days=int(self.daysToProccess))
        limitDate=True        
        for line in open(fileName).readlines():
            index+=1
            print index
            if re.match("^#|^Trace|^Stack|^$", line):
                continue
            try:
                _date=dt.strptime(line[:10].strip(), "%Y-%m-%d")
            
            except:
                _date=False
            print _date
            if limitDate:
                if _date:
                    if _date>=toDate:
                        limitDate=False
                    else:
                        continue
                        
            if _date:
                if len(multiline)>=1:
                    multilineString=self.getMultiline(multiline)
                    if re.match(r'^(.+?)\:(.|\n)*?\'(.+?)\'.*\'(.+?)\'.*in(.*)\:(.*)', multilineString[26:].strip()):
                        _match=re.match(r'^(.+?)\:(.|\n)*?\'(.+?)\'.*\'(.+?)\'.*in(.*)\:(.*)', multilineString[26:].strip())
                    elif re.match(r'^(.+?)\:()()()()()', multilineString[26:].strip()):
                        _match=re.match(r'^(.+?)\:()()()()()', multilineString[26:].strip()) 
                    parse=list(_match.groups())   
                    log=logRecord()
                    log.setSystem("2")
#                     print multilineString
                    log.setTimestamp(multilineString[:10].strip())
                    log.setType(parse[0])
                    log.setTypeError(parse[2])
                    log.setMessage(multilineString[26:].split(":",1)[-1])
                    log.setPath(parse[4])
                    log.setlineNumber(parse[5])
                    log.setLine(multilineString)
                    self.database.insert(log)

                    multiline=[]
                    multiline.append(line)
                else:
                    multiline.append(line) 
                    
            else:
                multiline.append(line)
                

    def analysisSystem(self,fileName):
        multiline=[]
        currentLine=''
        index=0
        
        toDate=dt.today()- timedelta(days=int(self.daysToProccess))
        limitDate=True        
        for line in open(fileName).readlines():
            index+=1
            print index
            if (limitDate):
                try:
                    _date=dt.strptime(line[:10].strip(), "%Y-%m-%d")
                except:
                    continue
                if _date>=toDate:
                    limitDate=False
                else:
                    continue
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
            log.setTimestamp(previusLine[:10].strip())
            parse= previusLine[26:].split(":")
            path = re.search('in (/.*?\s)', parse[-1])
            _path=path.group(1) if path else ''
            lineNumber= re.search('line (.*)(?<=\D)(\d+)', parse[-1])
            _lineNumber=lineNumber.group(2) if lineNumber else ''            
            log.setLine(previusLine)
            log.setParse(parse)
            log.setPath(_path)
            log.setlineNumber(_lineNumber)
            if "DEBUG" in previusLine:
                log.isDebug()
            else:
                log.isLog()
            self.database.insert(log)
    def getMultiline(self,multiline):
        multilineString=''
        for line in multiline:
            multilineString+=line
        return multilineString    
    def run(self):
        for fileName in glob.glob(self.filesPath+'*.*'):
            print fileName
            if os.path.basename(fileName).startswith('exception'):
                self.analysisException(fileName)
            if os.path.basename(fileName).startswith('system'):
                self.analysisSystem(fileName)                
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    path = config.get('config', "path")
    daysToProccess = config.get('config', "daysToProccess")
       
    cleaner = cleanlog(path,daysToProccess)
    cleaner.run()
            
            