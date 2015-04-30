import glob
import sqlite3
import re
import ConfigParser
from datetime import datetime as dt
from datetime import date, timedelta
import string
import ast
import time



class BackwardsReader:
    """Read a file line by line, backwards"""
    BLKSIZE = 4096

    def readline(self):
        BLKSIZE = 4096
        buf = ""
        self.file.seek(-1, 2)
        lastchar = self.file.read(1)
        trailing_newline = (lastchar == "\n")        
        while 1:
            newline_pos = buf.rfind("\n")
            pos = self.file.tell()
            if newline_pos != -1:
                # Found a newline
                line = buf[newline_pos+1:]
                buf = buf[:newline_pos]
                if pos or newline_pos or trailing_newline:
                    line += "\n"
                yield line
            elif pos:
                # Need to fill buffer
                toread = min(BLKSIZE, pos)
                self.file.seek(pos-toread, 0)
                buf = self.file.read(toread) + buf
                self.file.seek(pos-toread, 0)
                if pos == toread:
                    buf = "\n" + buf
            else:
                # Start-of-file
                return
    def __init__(self, _file):
        self.file = _file
        self.buf = ""
        self.file.seek(-1, 2)
        self.trailing_newline = 0
        lastchar = self.file.read(1)
        if lastchar == "\n":
            self.trailing_newline = 1
            self.file.seek(-1, 2)

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
        return [self.system,self.timeStamp,self.type,self.typeError,self.line,self.message,self.path,self.lineNumber]
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
#         self.backwardsReader=backwardsReader
    def analysisException(self,fileName):
        multiline=[]
        currentLine=''
        index=0
        start = time.time()
        print start
        
        toDate=dt.today()- timedelta(days=int(self.daysToProccess))
        limitDate=True        
        for line in open(fileName).readlines():
            index+=1
            print index
            if re.match("^#|^Trace|^Stack|^$", line):
                continue
# #             if (limitDate):
            try:
                _date=dt.strptime(line[:10].strip(), "%Y-%m-%d")
            except:
                _date=False
#                 continue
#                     continue
#                 if _date>=toDate:
#                     limitDate=False
#                     end = time.time()
#                     print end
#                     print end-start
#                     print index
#                 else:
#                     continue
            previusLine=currentLine           
            currentLine=line
                        
            if not _date:
                multiline.append(previusLine)
                continue
            else:
                if len(multiline)>1:
                    multilineString=self.getMultiline(multiline)
                    previusLine=multilineString
                else:
                    continue
                multiline=[]        
            log=logRecord()
            log.setSystem("2")
            log.setTimestamp(previusLine[:10].strip())
            parse=re.match(r'^(.+?)\:(.|\n)*?\'(.+?)\'.*\'(.+?)\'.*in(.*)\:(.*)', previusLine[10:])
            print previusLine
            print list(parse.groups())
#             if parse is None:
#             parse=re.search(r'^(.+?)\:\w*(.+?)\:(.*)$', previusLine[10:])
#             print previusLine[10:]
            if parse is not None:
                print list(parse.groups())
                break
            if "DEBUG" not in previusLine:
                print previusLine.strip()
#             parse= previusLine[26:].split(":")
#             log.setLine(previusLine)
#             log.setParse(parse)
#             log.setPath()
#             log.setlineNumber()
#             if "DEBUG" in previusLine:
#                 log.isDebug()
#             else:
#                 log.isLog()
#             self.database.insert(log)
#         print time.time()-start


    def analysisSystem(self,fileName):
        multiline=[]
        currentLine=''
        index=0
        start = time.time()
        print start
        
        toDate=dt.today()- timedelta(days=int(self.daysToProccess))
        limitDate=True        
        for line in open(fileName).readlines():
            index+=1
#             print index
            if (limitDate):
                try:
                    _date=dt.strptime(line[:10].strip(), "%Y-%m-%d")
                except:
                    continue
                if _date>=toDate:
                    limitDate=False
                    end = time.time()
                    print end
                    print end-start
                    print index
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
            log.setLine(previusLine)
            log.setParse(parse)
            log.setPath()
            log.setlineNumber()
            if "DEBUG" in previusLine:
                log.isDebug()
            else:
                log.isLog()
            self.database.insert(log)
        print time.time()-start        
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
        fileName='/Users/carlos/Downloads/tmp/exception.log'
        self.analysisException(fileName)
#         self.analysisSystem(fileName)
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    path = config.get('config', "path")
    daysToProccess = config.get('config', "daysToProccess")
       
    cleaner = cleanlog(path,daysToProccess)
    cleaner.run()
            
            