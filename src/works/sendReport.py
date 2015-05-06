import glob
import sqlite3
import re
import ConfigParser
from datetime import datetime as dt
from datetime import timedelta
import time
import os
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('./log.db')
        self.cursor = self.connection.cursor()
    def getCount(self,fromDate,toDate):
        query="""
select 
timeStamp as "Date"
,SUM(CASE log.type WHEN 'DEBUG (7)' THEN 1 ELSE 0 END) AS "DEBUG" 
,SUM(CASE log.type WHEN 'ERR (3)' THEN 1 ELSE 0 END) AS "ERR" 
,SUM(CASE log.type WHEN 'CRIT (2)' THEN 1 ELSE 0 END) AS "CRIT"
,count(*) as "Total"
 from log  where timeStamp between (?) and (?) group by timeStamp order by timeStamp desc        
        
        """
        self.cursor.execute(query,(toDate,fromDate,))        
        html='<table>'
        html+='<tr><td>Date</td><td>DEBUG</td><td>ERR</td><td>CRIT</td><td>Total</td></tr>'  
        for row in self.cursor.fetchall(): 
            try:           
                html+= '<tr>{}</tr>'.format(''.join(['<td>{}</td>\n'.format(unicode(str(col), 'utf-8')) for col in row]))
            except:
                continue 
        html+='</table>'
        return html
    def getMessages(self,fromDate,toDate):
        query="select message,count(*)as 'Count' from log where timeStamp between (?) and (?) and not( systemId='1' and type='DEBUG (7)') group by  message order by Count desc" 
        self.cursor.execute(query,(toDate,fromDate,))
        html='<table>'  
        for row in self.cursor.fetchall(): 
            try:           
                html+= '<tr>{}</tr>'.format(''.join(['<td>{}</td>\n'.format(unicode(str(col), 'utf-8')) for col in row]))
            except:
                continue 
        html+='</table>'
        return html
class Report:
    def __init__(self,fromDate,toDate):
        self.fromDate=fromDate
        self.toDate=toDate
        self.data=Database()
    def run(self):
        html=""
        html+=  self.data.getCount(self.fromDate,self.toDate)
        html+=  self.data.getMessages(self.fromDate,self.toDate)


        fromaddr = 'cespinosa@v2.com'
        toaddrs  = 'carlos.espinosa@outlook.com'
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Error Report"
        msg['From'] = fromaddr
        msg['To'] = toaddrs        
        
        # Credentials (if needed)
        username = 'cespinosa@v2.com'
        password = '@#$5M0k137'
        htmlpart = MIMEText(html, 'html')
        msg.attach(htmlpart)
        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()
        
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    path = config.get('config', "path")
    daysToProccess = config.get('config', "daysToProccess")
    toDate=dt.today()- timedelta(days=int(daysToProccess))
    
    
    reporter = Report(dt.today().date(),toDate.date())
    reporter.run()        