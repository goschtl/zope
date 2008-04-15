# Display a list of active sessions

from datetime import datetime
from time import localtime, time

from zope.publisher.browser import BrowserPage
from zope.app.authentication.helpers import getSessionRecords

from zope.app.pagetemplate import ViewPageTemplateFile

def formattimestamp(ts):
    lt = localtime(ts)
    dt = datetime(lt[0], lt[1], lt[2], lt[3], lt[4])
    return dt.strftime('%Y-%m-%d %H:%M')

class ActiveSessions(BrowserPage):

    __call__ = ViewPageTemplateFile('activesessions.pt')

    def SessionRecords(self):
        data = []
        timeNow = time()
        for row in getSessionRecords(self.context):
            idleTime = 'not used'
            if row['accessTime']:
                idleTime = int(timeNow - row['accessTime'])
            data.append( {
                'domain': row['domain'],
                'login': row['login'],
                'ip': row['ip'],
                'extractTime': formattimestamp(row['extractTime']),
                'idleTime': idleTime,
            })
        return data

