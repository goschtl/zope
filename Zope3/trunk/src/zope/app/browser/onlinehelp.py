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

$Id: onlinehelp.py,v 1.12 2003/07/30 01:06:05 rogerineichen Exp $
"""
from zope.interface import providedBy

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.component import getService, getView
from zope.component.view import viewService
from zope.publisher.browser import BrowserView
from zope.app.traversing import getRoot
from zope.app.context import ContextWrapper
from zope.app.traversing import getParents, getName
from zope.proxy import removeAllProxies

class OnlineHelpTopicView(BrowserView):

    def _makeSubTree(self, topic):
        html = '<ul>\n'
        for entry in topic.items():
            entry = ContextWrapper(entry[1], topic, name=entry[0]) 
            html += '  <li><a href="%s">%s</a></li>\n' %(
                getView(entry, 'absolute_url', self.request)(),
                entry.getTitle())
            html += self._makeSubTree(entry)
        html += '</ul>\n'
        return html

    def getTopicTree(self):
        onlinehelp = getRoot(self.context)
        return self._makeSubTree(onlinehelp)


class FindRelevantHelpTopics(BrowserView):
    """This object is used as a view on a view, so that we can get all the
    required information."""

    def __call__(self):

        class FindResult:
            def __init__(self, url, topic):
                self.url = url
                self.topic = topic

        view_class = self.context.__class__
        obj = self.context.context
        help = getService(obj, 'OnlineHelp')
        ifaces = providedBy(obj).flattened()
        topics = []
        for iface in ifaces:
            specs = viewService.getRegisteredMatching((iface,),
                                                      IBrowserPresentation)
            for spec in specs:
                if spec[2][0] is not view_class:
                    continue
                for topic in help.getTopicsForInterfaceAndView(iface, spec[4]):
                    parents = getParents(topic)
                    path = map(getName, [topic]+parents[:-1]) 
                    path.reverse()
                    url = getView(obj, 'absolute_url', self.request)()
                    url += '/++help++/++skin++Onlinehelp/'+'/'.join(path)
                    topics.append(FindResult(url, topic))
        
        return topics
        
