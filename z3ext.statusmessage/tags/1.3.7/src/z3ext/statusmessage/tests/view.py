##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope.app.pagetemplate import ViewPageTemplateFile
from z3ext.statusmessage.interfaces import IStatusMessage


class TestView(object):

    index = ViewPageTemplateFile('test.pt')

    def __call__(self):
        return self.index()

    def test(self):
        IStatusMessage(self.request).add('Test message')
        return self.index()

    def redirect(self):
        IStatusMessage(self.request).add('Test message with redirect')
        self.request.response.redirect('test.html')
