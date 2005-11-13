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
"""Simple Text Controller implementation.

$Id$
"""
__docformat__ = "reStructuredText"
import types
import zope.interface

from zope.tutorial import interfaces

class SimpleCLIController(object):
    """A dummy Command-line based controller.

    Instead of running the tests, this controller simply displays the text and
    examples. This makes this controller well-suited for testing.
    """
    #zope.interface.implements(interfaces.ITutorialController)

    PYTHON_PROMPT = '>>> '
    PYTHON_CONTINUE = '... '

    def __init__(self, session):
        self.session = session
        self.running = False

    def start(self):
        """See interfaces.ITutorialController"""
        self.running = True
        print 'Starting Tutorial: ' + self.session.tutorial.title

    def end(self):
        """See interfaces.ITutorialController"""
        print '---------- The End ----------'
        self.running = False

    def display(self, text):
        """See interfaces.ITutorialController"""
        print
        print text.strip()
        print

    def run(self, example):
        """See interfaces.ITutorialController"""
        # Prepare the source and print it
        source = example.source.strip()
        source = ' '*example.indent + self.PYTHON_PROMPT + source
        source = source.replace(
            '\n', '\n' + ' '*example.indent + self.PYTHON_CONTINUE)
        print source

        # Prepare the expected output and print it
        if example.want:
            want = example.want.strip()
            want = ' '*example.indent + want
            want = want.replace('\n', '\n' + ' '*example.indent)
            print want

    def doNextStep(self):
        """See interfaces.ITutorialController"""
        step = self.session.getNextStep()
        if isinstance(step, types.StringTypes):
            self.display(step)
        elif step is None:
            self.end()
        else:
            self.run(step)
