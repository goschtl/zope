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

$Id$
"""
from zope.proxy import removeAllProxies
from zope.interface import providedBy
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app import zapi
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.onlinehelp.interfaces import IOnlineHelpTopic

class OnlineHelpTopicView(object):
    """View for one particular help topic."""

    def __init__(self, context, request, base_url=''):
        self.context = context
        self.request = request
        self.base_url = base_url
        self.onlinehelp = removeAllProxies(zapi.getRoot(self.context))
        if base_url == '':
            self.base_url = zapi.getPath(self.onlinehelp.context)+"/++help++"

    def getTopicTree(self):
        """ return the tree of help topics."""
        self.context = zapi.getRoot(self.context)
        return self.subtopics()

    def getContextHelpTopic(self):
        """ Retrieve a help topic based on the context of the
        help namespace.

        If the context is a view, try to find
        a matching help topic for the view and its context.
        If not help topic is found, try got get a help topic for
        and interface only.

        If the context is not a view, try to retrieve a help topic
        for an interface only.

        If nothing is found, return the onlinehelp root topic

        """
        help_context = self.onlinehelp.context
        topic = self.context
        if IBrowserView.providedBy(help_context):
            # called from a view
            for iface in providedBy(zapi.getParent(help_context)):
                # try for interface and view match
                topics = self.onlinehelp.getTopicsForInterfaceAndView(
                    iface,
                    zapi.getName(help_context)
                    )
                if len(topics)>0:
                    topic = topics[0]
                    break
            if topic == self.context:
                # nothing found for view try iface only
                for iface in providedBy(zapi.getParent(help_context)):
                    topics = self.onlinehelp.getTopicsForInterfaceAndView(
                        iface,
                        None
                        )
                    if len(topics)>0:
                        topic = topics[0]
                        break
        else:
            # called without view
            for iface in providedBy(help_context):
                topics = self.onlinehelp.getTopicsForInterfaceAndView(
                    iface,
                    None
                    )
                if len(topics)>0:
                    topic = topics[0]
                    break
                
        # XXX returns only the first of the matching topics.
        #     The page template only processes one topic
        return topic

    def listHelpItems(self):
        """ recurse through the help topic tree"""
        # 
        children=[]
        for name, helpitem in self.context.items():
            info={}
            info['title'] = helpitem.title
            info['path'] = self.base_url+'/'+name
            topic = OnlineHelpTopicView(
                helpitem,
                self.request,
                self.base_url+'/'+name)

            info['topics']=topic.subtopics()
            children.append(info)

        return children

    subtopics = ViewPageTemplateFile('topiclink.pt')



