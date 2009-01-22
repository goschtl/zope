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
from zope import interface
from zope.app.pagetemplate import ViewPageTemplateFile
from z3ext.statusmessage.message import Message
from z3c.form.interfaces import IErrorViewSnippet


class FormErrorStatusMessage(Message):

    index = ViewPageTemplateFile('browser/message.pt')

    @property
    def context(self):
        return self

    def render(self, message):
        self.message = message[0]
        self.errors = [err for err in message[1:] 
                       if IErrorViewSnippet.providedBy(err) and err.widget is None]
        return self.index()
