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
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""

Revision information:
$Id: testZPTPageEval.py,v 1.4 2002/07/17 16:54:18 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.App.OFS.Content.ZPTPage.Views.Browser.ZPTPageEval import ZPTPageEval
from Zope.Proxy.ContextWrapper import ContextWrapper


class Test(CleanUp, TestCase):

    def test(self):

        class Template:
            def render(self, request, **kw):
                self.called = request, kw
                return 42

            content_type = 'text/x-test'

        class Folder: name='zope'
        folder = Folder()
        
        class Request(object):
            def _getResponse(self):
                return self

            response = property(_getResponse)
            
            def setHeader(self, name, value):
                setattr(self, name, value)
                           
        request = Request()

        template = ContextWrapper(Template(), folder)

        view = ZPTPageEval(template, None)
        self.assertEqual(view.index(request), 42)
        self.assertEqual(template.called, (request, {}))
        self.assertEqual(getattr(request, 'content-type'), 'text/x-test')

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
