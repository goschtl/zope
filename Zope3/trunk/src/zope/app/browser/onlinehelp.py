##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""OnlineHelp views

$Id: onlinehelp.py,v 1.16 2003/10/16 10:15:45 jim Exp $
"""
from zope.interface import providedBy

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.component import getService, getView
from zope.component.view import viewService
from zope.app.publisher.browser import BrowserView
from zope.app.traversing import getRoot
from zope.app.traversing import getParents, getName

class OnlineHelpTopicView(BrowserView):
    """View for one particular help topic."""

    def _makeSubTree(self, topic):
        html = '<ul>\n'
        for entry in topic.items():
            html += '  <li><a href="%s">%s</a></li>\n' %(
                getView(entry, 'absolute_url', self.request)(),
                entry.getTitle())
            html += self._makeSubTree(entry)
        html += '</ul>\n'
        return html

    def getTopicTree(self):
        onlinehelp = getRoot(self.context)
        return self._makeSubTree(onlinehelp)

