##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""mail ZCML Namespace handler

$Id: metaconfigure.py,v 1.3 2003/06/23 15:45:39 alga Exp $
"""

from zope.component import getService
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.metaconfigure import provideService
from zope.app.mail.service import QueuedMailService, DirectMailService
from zope.app.mail.service import QueueProcessorThread
from zope.app.mail.mailer import SendmailMailer, SMTPMailer


def queuedService(_context, permission, queuePath, mailer, name="Mail"):
    # XXX what if queuePath is relative?  I'd like to make it absolute here,
    # but should it be relative to $CWD or $INSTANCE_HOME (if there is one
    # in Zope 3)?

    def createQueuedService():
        component = QueuedMailService(queuePath)
        provideService(name, component, permission)

        thread = QueueProcessorThread()
        thread.setMailer(getMailer(mailer))
        thread.setQueuePath(queuePath)
        thread.setDaemon(True)
        thread.start()

    return [
        Action(
            discriminator = ('service', name),
            callable = createQueuedService,
            args = (),
            )
        ]

def directService(_context, permission, mailer, name="Mail"):

    def makeService():
        mailer_component = queryMailer(mailer)
        if mailer_component is None:
            raise ConfigurationError("Mailer %r is not defined" % mailer)
        component = DirectMailService(mailer_component)
        provideService(name, component, permission)

    return [
        Action(
            discriminator = ('service', name),
            callable = makeService,
            args = (),
            )
        ]


def sendmailMailer(_context, id,
                   command="/usr/lib/sendmail -oem -oi -f %(from)s %(to)s"):
    return [Action(discriminator=('mailer', id),
                   callable=provideMailer,
                   args=(id, SendmailMailer(command)),)
        ]


def smtpMailer(_context, id, hostname="localhost", port="25",
               username=None, password=None):
    return [Action(discriminator=('mailer', id),
                   callable=provideMailer,
                   args=(id, SMTPMailer(hostname, port,
                                          username, password)),)
        ]

# Example of mailer configuration:
#
#   def smtp(_context, id, hostname, port):
#       component = SMTPMailer(hostname, port)
#       if queryMailer(id) is not None:
#           raise ConfigurationError("Redefinition of mailer %r" % id)
#       provideMailer(id, component)
#       return []
#
# or is it better to make mailer registration an Action?  But that won't work,
# because queryMailer will get called during directive processing, before any
# actions are run.


mailerRegistry = {}
queryMailer = mailerRegistry.get
provideMailer = mailerRegistry.__setitem__

def getMailer(mailer):
    result = queryMailer(mailer)
    if result is None:
        raise ConfigurationError("Mailer lookup failed")
    return result

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    addCleanUp(mailerRegistry.clear)
    del addCleanUp
