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

$Id$
"""
import os

import zope.app
from zope.app import zapi
from zope.app.container.sample import SampleContainer
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing import traverse

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic, IOnlineHelp
from zope.interface import implements

class OnlineHelpTopic(SampleContainer):
    __doc__ = IOnlineHelpTopic.__doc__

    implements(IOnlineHelpTopic)

    title = u""

    def __init__(self, title, path, doc_type='txt'):
        """Initialize object."""
        self.title = title
        self.setContentPath(path, doc_type)
        super(OnlineHelpTopic, self).__init__()

    def setContentPath(self, path, doc_type='txt'):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        self._content_path = path
        self._doc_type = doc_type

    def getContent(self):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelpTopic"
        raw = open(self._content_path).read()

        if self._doc_type == 'txt':
            # XXX This should be cleaned up when reST is implemented
            raw = raw.replace('<', '&lt;')
            raw = raw.replace('>', '&gt;')
            raw = '<p>' + raw.replace('\n\n', '\n</p><p>') + '</p>'
            raw = raw.replace('\n', '<br>')
            raw = raw.replace('  ', '&nbsp;&nbsp;')
            return raw
        else:
            return raw


class OnlineHelp(OnlineHelpTopic):
    __doc__ = IOnlineHelp.__doc__

    implements(IOnlineHelp, IContainmentRoot)

    def __init__(self, title, path, doc_type='txt'):
        self._registry = {}
        super(OnlineHelp, self).__init__(title, path, doc_type)

    def getTopicsForInterfaceAndView(self, interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        return self._registry.get((interface, view), [])

    def registerHelpTopic(self, parent_path, id, title,
                          doc_path, doc_type='txt', interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        parent = traverse(self, parent_path)
        # Create and add topic
        parent[id] = OnlineHelpTopic(title, doc_path, doc_type)
        topic = parent[id]
        # Add topic to registry
        if interface is not None:
            if not self._registry.has_key((interface, view)):
                self._registry[(interface, view)] = []
            self._registry[(interface, view)].append(topic)

# Global Online Help
path = os.path.join(os.path.dirname(zope.app.__file__),
                    'onlinehelp', 'welcome.txt')
help = OnlineHelp('Online Help', path)
