 ##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Implementation of OnlineHelp System.

This the default implmentation of the OnlineHelp. It defines the global
OnlineHelp in which all basic Zope-core help screens are registered.

$Id: __init__.py,v 1.3 2003/03/24 13:45:34 stevea Exp $
"""
import os
from zope.app.container.sample import SampleContainer
from zope.app.traversing import traverse, getParent, objectName
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.traversing.adapters import Traverser
import zope.app
from zope.proxy.context import ContextWrapper

from zope.app.interfaces.onlinehelp import IOnlineHelpTopic, IOnlineHelp

class OnlineHelpTopic(SampleContainer):
    __doc__ = IOnlineHelpTopic.__doc__

    __implements__ =  IOnlineHelpTopic

    def __init__(self, title, path, doc_type='txt'):
        """Initialize object."""
        self.title = title
        self.setContentPath(path, doc_type)
        super(OnlineHelpTopic, self).__init__()

    def setTitle(self, title):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        self._title = title

    def getTitle(self):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        return self._title

    title = property(getTitle, setTitle, None)

    def setContentPath(self, path, doc_type='txt'):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        self._content_path = path
        self._doc_type = doc_type

    def getContent(self):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        raw = open(self._content_path).read()
        
        if self._doc_type == 'txt':
            return '<p>' + raw.replace('\n\n', '\n</p><p>') + '</p>'
        else:
            return raw


class OnlineHelp(OnlineHelpTopic):
    __doc__ = IOnlineHelp.__doc__

    __implements__ =  IOnlineHelp, IContainmentRoot

    def __init__(self, title, path, doc_type='txt'):
        self._registry = {}
        super(OnlineHelp, self).__init__(title, path, doc_type)

    def getTopicsForInterfaceAndView(self, interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        return self._registry.get((interface, view), [])

    def registerHelpTopic(self, parent_path, id, title,
                          doc_path, doc_type='txt', interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        #parent = traverse(self, parent_path)
        parent = Traverser(self).traverse(parent_path)
        # Create and add topic
        id = parent.setObject(id, OnlineHelpTopic(title, doc_path, doc_type))
        topic = ContextWrapper(parent[id], parent, name=id)
        # Add topic to registry
        if not self._registry.has_key((interface, view)):
            self._registry[(interface, view)] = []
        self._registry[(interface, view)].append(topic)

    def unregisterHelpTopic(self, topic_path):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        # Delete topic from tree
        topic = Traverser(self).traverse(topic_path)
        name = objectName(topic)
        parent = getParent(topic)
        del parent[name]
        # unregister from registry
        for item in registry.items():
            if topic in item[1]:
                item[1].remove(topic)

# Global Online Help
path = os.path.join(os.path.dirname(zope.app.__file__),
                    'onlinehelp', 'welcome.txt')
help = OnlineHelp('Online Help', path)
