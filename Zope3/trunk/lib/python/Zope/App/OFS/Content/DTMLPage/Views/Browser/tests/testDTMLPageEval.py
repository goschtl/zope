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

$Id: testDTMLPageEval.py,v 1.1 2002/07/11 00:17:02 srichter Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.App.OFS.Content.DTMLPage.Views.Browser.DTMLPageEval import \
     DTMLPageEval
from Zope.Proxy.ContextWrapper import ContextWrapper


class Test(CleanUp, TestCase):

    def test(self):

        class Template:
            def render(self, request, **kw):
                self.called = request, kw
                request.response.setHeader('content-type', self.content_type)
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

        view = DTMLPageEval(template, None)
        self.assertEqual(view.index(request), 42)
        self.assertEqual(template.called, (request, {}))
        self.assertEqual(getattr(request, 'content-type'), 'text/x-test')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
