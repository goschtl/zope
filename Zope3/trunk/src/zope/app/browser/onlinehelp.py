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

$Id: onlinehelp.py,v 1.3 2003/04/30 23:37:48 faassen Exp $
"""
from zope.interface.implements import flattenInterfaces

from zope.component import getService, getView
from zope.publisher.browser import BrowserView
from zope.app.traversing import getRoot
from zope.proxy.context import ContextWrapper
from zope.app.traversing import getParents, objectName
from zope.proxy.introspection import removeAllProxies

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

        view = self.context
        obj = view.context
        help = getService(obj, 'OnlineHelp')
        ifaces = flattenInterfaces(removeAllProxies(obj.__implements__))
        topics = []
        for klass in view.__class__.__bases__ + (view.__class__, None):
            for iface in ifaces:
                for topic in help.getTopicsForInterfaceAndView(iface, klass):
                    parents = getParents(topic)
                    path = map(objectName, parents[:-1]+[topic]) 
                    url = getView(obj, 'absolute_url', self.request)()
                    url += '/++help++/'+'/'.join(path)
                    topics.append(FindResult(url, topic))
        
        return topics
        
