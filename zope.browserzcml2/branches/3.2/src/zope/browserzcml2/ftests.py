##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Tests

$Id$
"""
import unittest
import zope.formlib.interfaces
import zope.interface
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.testing.functional import FunctionalDocFileSuite

class MacGyverPage(zope.formlib.Page):
    def __call__(self):
        return u"I've got a Swiss Army knife"

@zope.interface.implementer(zope.formlib.interfaces.IPage)
def makeAMacGyverPage(context, request):
    return MacGyverPage(context, request)

class MacGyverTemplatePage(zope.formlib.Page):
    __call__ = ViewPageTemplateFile('test.pt')

class JackDaltonTemplatePage(zope.formlib.Page):
    __call__ = ViewPageTemplateFile('test2.pt')
    def getName(self):
        return u'Jack Dalton'

class PhoenixPages(object):
    macgyver = ViewPageTemplateFile('test.pt')
    def pete(self):
        return u'Peter Thornton'

def test_suite():
    return unittest.TestSuite([
        FunctionalDocFileSuite('ftest.txt')
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
