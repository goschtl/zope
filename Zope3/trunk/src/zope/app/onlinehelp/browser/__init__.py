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

class TopicTreeView(object):

    def __init__(self, context, request, base_url=''):
        self.context = context
        self.treecontext = context
        self.request = request
        self.base_url = base_url

    def getTopicTree(self):
        """ return the tree of help topics."""
        # set up the root values
        if self.base_url == '':
            self.base_url = '/++help++'
        self.treecontext = zapi.getService("OnlineHelp")
        return self.subtopics()

    def listHelpItems(self):
        """ recurse through the help topic tree"""
        children=[]
        for name, helpitem in self.treecontext.items():
            info={}
            info['title'] = helpitem.title
            info['path'] = self.base_url+'/'+name
            topic = TopicTreeView(
                helpitem,
                self.request,
                self.base_url+'/'+name)

            info['topics']=topic.subtopics()
            children.append(info)

        return children

    subtopics = ViewPageTemplateFile('topiclink.pt')


class OnlineHelpTopicView(TopicTreeView):
    """View for one particular help topic."""

    def __init__(self, context, request):
        super(OnlineHelpTopicView, self).__init__(context, request)
        self.context = context
        self.request = request

    def renderTopic(self):
        """ render the source of the help topic """
        source = zapi.createObject(None,
                                   self.context.type,
                                   self.context.source)
        view = zapi.getView(removeAllProxies(source), '', self.request)
        html = view.render()
        return html

class ContextHelpView(TopicTreeView):

    def __init__(self, context, request):
        super(ContextHelpView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.topic = None

    def renderContextTopic(self):
        """ retrieve and render the source of a context help topic """
        topic = self.getContextHelpTopic()
        source = zapi.createObject(None,
                                   topic.type,
                                   topic.source)
        view = zapi.getView(removeAllProxies(source), '', self.request)
        html = view.render()
        return html

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
        if self.topic is not None:
            return self.topic

        onlinehelp = zapi.getService("OnlineHelp")
        help_context = onlinehelp.context
        self.topic = self.context
        if IBrowserView.providedBy(help_context):
            # called from a view
            for iface in providedBy(zapi.getParent(help_context)):
                # try for interface and view match
                topics = onlinehelp.getTopicsForInterfaceAndView(
                    iface,
                    zapi.getName(help_context)
                    )
                if len(topics)>0:
                    self.topic = topics[0]
                    break
            if self.topic == self.context:
                # nothing found for view try iface only
                for iface in providedBy(zapi.getParent(help_context)):
                    topics = onlinehelp.getTopicsForInterfaceAndView(
                        iface,
                        None
                        )
                    if len(topics)>0:
                        self.topic = topics[0]
                        break
        else:
            # called without view
            for iface in providedBy(help_context):
                topics = onlinehelp.getTopicsForInterfaceAndView(
                    iface,
                    None
                    )
                if len(topics)>0:
                    self.topic = topics[0]
                    break

        # XXX returns only the first of the matching topics.
        #     The page template only processes one topic
        return self.topic



