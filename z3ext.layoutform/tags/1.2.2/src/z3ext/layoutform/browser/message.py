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
from zope import component, interface
from zope.app.pagetemplate import ViewPageTemplateFile
from z3ext.statusmessage.interfaces import IMessageView
from z3ext.layoutform.interfaces import IFormErrorStatusMessage


class Message(object):
    interface.implements(IMessageView)
    component.adapts(IFormErrorStatusMessage, interface.Interface)

    index = ViewPageTemplateFile('message.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        return self.index()
