##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Docstring tests for the wiki package.

$Id$
"""
import unittest
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import VocabularyRegistry, _clear
from zope.schema.vocabulary import getVocabularyRegistry
from zope.schema.vocabulary import setVocabularyRegistry
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.testing import placelesssetup, ztapi

from zwiki.interfaces import IComment


class DCStub(object):

    def __init__(self, context):
        self.context = context

    def getTitle(self):
        return getattr(self.context, 'dc_title', u'')

    def setTitle(self, title):
        self.context.dc_title = title

    title = property(getTitle, setTitle)

def VocabularyFactory(context):
    return SimpleVocabulary.fromValues(('zope.source.rest', 'zope.source.stx'))


def setUp(test):
    placelesssetup.setUp()
    ztapi.provideAdapter(IComment, ICMFDublinCore, DCStub)

    _clear()
    registry = VocabularyRegistry()
    registry.register('SourceTypes', VocabularyFactory)
    setVocabularyRegistry(registry)


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zwiki.comment',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('zwiki.wikipage',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
