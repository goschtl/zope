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
"""Tests creator annotation.

$Id: test_creatorannotator.py,v 1.1 2003/03/27 12:51:47 ctheune Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.testing.cleanup import CleanUp

from zope.interface import Interface
from zope.component.adapter import provideAdapter

from zope.app.interfaces.annotation import IAnnotations
from zope.app.dublincore.creatorannotator import CreatorAnnotator
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.security import IPrincipal
from zope.app.interfaces.event import IEvent
from zope.security.management import noSecurityManager, newSecurityManager

class IDummyContent(Interface):
    pass

class DummyEvent:
    __implements__ = IEvent

class DummyDCAdapter(object):

    __used_for__ = IDummyContent
    __implements__ = IZopeDublinCore

    def _getcreator(self):
        return self.context.creators

    def _setcreator(self, value):
        self.context.creators = value
    creators = property(_getcreator,_setcreator,None,"Adapted Creators")

    def __init__(self, context):
        self.context = context
        self.creators = context.creators


class DummyDublinCore:

    __implements__ = IDummyContent

    creators = ()

class DummyPrincipal:
    __implements__ = IPrincipal

    def getId(self):
        return self._id

    def getTitle(self):
        return self._title

    def getDescription(self):
        return self._description

    def getRoles(self):
        return self._roles

class Test(PlacefulSetup, TestCase, CleanUp):

    def setUp(self):
        PlacefulSetup.setUp(self)
        provideAdapter(IDummyContent, IZopeDublinCore, DummyDCAdapter)
        noSecurityManager()
        
    def tearDown(self):
        noSecurityManager()
        PlacefulSetup.tearDown(self)

    def test_creatorannotation(self):

        # Create stub event and DC object
        event = DummyEvent()
        data = DummyDublinCore()
        event.object = data

        good_author = DummyPrincipal()
        good_author._id = 'goodauthor'
        good_author._title = 'the good author'
        good_author._description = 'this is a very good author'
        good_author._roles = []

        bad_author = DummyPrincipal()
        bad_author._id = 'badauthor'
        bad_author._title = 'the bad author'
        bad_author._description = 'this is a very bad author'
        bad_author._roles = []

        # Check what happens if no user is there
        noSecurityManager()
        CreatorAnnotator.notify(event)
        self.assertEqual(data.creators,())

        # Let the bad edit it first
        security = newSecurityManager(bad_author)
        CreatorAnnotator.notify(event)

        self.failIf(len(data.creators) != 1)
        self.failUnless(bad_author.getId() in data.creators)
        
        # Now let the good edit it
        security = newSecurityManager(good_author)
        CreatorAnnotator.notify(event)
        
        self.failIf(len(data.creators) != 2)
        self.failUnless(good_author.getId() in data.creators)
        self.failUnless(bad_author.getId() in data.creators)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
