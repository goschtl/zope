##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser View for the sub-thread of a Message or MessageBoard

$Id$
"""
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from book.messageboard.interfaces import IMessage

class Thread:

    def __init__(self, context, request, base_url=''):
        self.context = context
        self.request = request
        self.base_url = base_url

    def listContentInfo(self):
        children = []
        for name, child in self.context.items():
            if IMessage.providedBy(child):
                info = {}
                info['title'] = child.title
                url = self.base_url + name + '/'
                info['url'] = url + '@@thread.html'
                thread = Thread(child, self.request, url)
                info['thread'] = thread.subthread()
                children.append(info)
        return children

    subthread = ViewPageTemplateFile('subthread.pt')

