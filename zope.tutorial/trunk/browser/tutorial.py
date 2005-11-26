##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tutorial and Tutorial Manager views

$Id$
"""
__docformat__ = "reStructuredText"
import zope.proxy

from jsonserver.jsonrpc import MethodPublisher
from zope.app.basicskin.standardmacros import StandardMacros

class TutorialMacros(StandardMacros):
    """Page Template METAL macros for Tutorial"""
    macro_pages = ('runner_macros',)


class TutorialsRunner(object):

    pass


class TutorialSessionManager(MethodPublisher):

    def createSession(self):
        name = self.context.createSession()
        import zope.proxy
        zope.proxy.removeAllProxies(self.context[name]).initialize()
        return name

    def deleteSession(self, id):
        self.context.deleteSession(id)


class TutorialSession(MethodPublisher):

    def getCommand(self):
        return self.context.getCommand()

    def addResult(self, id, result):
        self.context.addResult(id, result)
        return True

    def keepGoing(self):
        return self.context.keepGoing()
