import logging
import Zope2
from zope.app.appsetup.interfaces import (DatabaseOpenedWithRoot,
                                          IDatabaseOpenedWithRootEvent)
from zope.event import notify
from zope.component import provideHandler


def notifyDBEvent(self):
    notify(DatabaseOpenedWithRoot(Zope2.DB))


def logToDbEvent(event):
    db = event.database
    log = logging.getLogger('Zope')
    log.info('%s zodb database opened with root' % db.database_name)

provideHandler(logToDbEvent, [IDatabaseOpenedWithRootEvent])
