##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""OnlineHelp views

$Id$
"""
from zope.app import zapi
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.interfaces.browser import IBrowserView

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic, IOnlineHelp
from zope.app.onlinehelp import getTopicFor

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
        self.treecontext = zapi.getUtility(IOnlineHelp,"OnlineHelp")
        return self.subtopics()

    topicTree = property(getTopicTree)

    def listHelpItems(self):
        """ recurse through the help topic tree"""
        children=[]
        for name, helpitem in self.treecontext.items():
            if IOnlineHelpTopic.providedBy(helpitem):
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
        view = zapi.getView(source, '', self.request)
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
        view = zapi.getView(source, '', self.request)
        html = view.render()
        return html

    def getContextHelpTopic(self):
        """ Retrieve a help topic based on the context of the
        help namespace.

        If the context is a view, try to find
        a matching help topic for the view and its context.
        If no help topic is found, try to get a help topic for
        the context only.

        If the context is not a view, try to retrieve a help topic
        based on the context.

        If nothing is found, return the onlinehelp root topic

        """
        if self.topic is not None:
            return self.topic

        onlinehelp = self.context
        help_context = onlinehelp.context
        self.topic = None
        if IBrowserView.providedBy(help_context):
            # called from a view
            self.topic = getTopicFor(
                zapi.getParent(help_context),
                zapi.getName(help_context)
                )
            if self.topic is None:
                # nothing found for view try context only
                self.topic = getTopicFor(
                    zapi.getParent(help_context)
                    )
        else:
            # called without view
            self.topic = getTopicFor(help_context)

        if self.topic is None:
            self.topic = onlinehelp

        return self.topic

    contextHelpTopic = property(getContextHelpTopic)

