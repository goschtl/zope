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
import thread
import types
import time
import zope.proxy

from jsonserver.jsonrpc import MethodPublisher
from zope.app.basicskin.standardmacros import StandardMacros
from zope.app.apidoc.utilities import renderText

from zope.tutorial import testbrowser
import zope.testbrowser

class TutorialMacros(StandardMacros):
    """Page Template METAL macros for Tutorial"""
    macro_pages = ('runner_macros',)


class TutorialsRunner(object):

    pass


class TutorialSessionManager(MethodPublisher):

    def createSession(self):
        name = self.context.createSession()
        self.context[name].initialize()
        return name

    def deleteSession(self, id):
        self.context.deleteSession(id)


def run(tutorial, example):
    OldBrowser = zope.testbrowser.Browser
    zope.testbrowser.Browser = testbrowser.Browser
    exec compile(example.source, '<string>', "single") in tutorial.globs
    # Eek, gotta remove the __builtins__
    del tutorial.globs['__builtins__']
    tutorial.locked = False
    zope.testbrowser.Browser = OldBrowser


class TutorialSession(MethodPublisher):

    def getNextStep(self):
        tutorial = zope.proxy.removeAllProxies(self.context)
        step = tutorial.getNextStep()
        if isinstance(step, types.StringTypes):
            text = renderText(step, format='zope.source.rest')
            return {'action': 'displayText',
                    'params': (text,)}
        elif step is None:
            return {'action': 'finishTutorial',
                    'params': ()}
        else:
            tutorial.locked = True
            testbrowser.State.reset()
            thread.start_new_thread(run, (tutorial, step))
            while tutorial.locked and not testbrowser.State.hasAction():
                time.sleep(0.1)
            return testbrowser.State.action

    def setCommandResult(self, result):
        testbrowser.State.result = result
        return True

    def keepGoing(self):
        return self.context.keepGoing()
