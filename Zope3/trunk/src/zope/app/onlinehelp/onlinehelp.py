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

This the default implementation of the OnlineHelp. It defines the global
OnlineHelp in which all basic Zope-core help screens are registered.

$Id$
"""
from zope.interface import implements, providedBy

from zope.app import zapi
from zope.app.traversing.interfaces import IContainmentRoot

from zope.app.onlinehelp.interfaces import IOnlineHelp
from zope.app.onlinehelp.onlinehelptopic import OnlineHelpTopic

class OnlineHelp(OnlineHelpTopic):
    """
    >>> import os
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import I1, Dummy1
    >>> path = os.path.join(testdir(), 'help.txt')

    Create an onlinehelp instance
    
    >>> onlinehelp = OnlineHelp('Help', path)

    First do the inteface verifing tests.
    
    >>> from zope.interface.verify import verifyObject
    >>> from zope.app.traversing.interfaces import IContainmentRoot
    >>> verifyObject(IOnlineHelp, onlinehelp)
    True
    >>> verifyObject(IContainmentRoot, onlinehelp)
    True

    Register a new subtopic for interface 'I1' and view 'view.html'
    
    >>> path = os.path.join(testdir(), 'help2.txt')
    >>> onlinehelp.registerHelpTopic('', 'help2', 'Help 2',
    ...     path, I1, 'view.html')

    Test if the subtopic is set correctly
    >>> onlinehelp['help2'].title
    'Help 2'

    >>> onlinehelp._registry[(I1, 'view.html')][0].title
    'Help 2'

    The help topic must be found if the onlinehelp is queried
    with interface and view name.
    
    >>> onlinehelp.getTopicsForInterfaceAndView(I1, 'view.html')[0].title
    'Help 2'

    If queried with an instance the help topic must still be found
    >>> onlinehelp.getTopicForObjectAndView(Dummy1(), 'view.html').title
    'Help 2'

    To register help for an interface only simple skip the view parameter
    while registering.
    >>> onlinehelp.registerHelpTopic('', 'help3', 'Help for Interface',
    ...     path, I1)
    >>> onlinehelp.getTopicForObjectAndView(Dummy1()).title
    'Help for Interface'

    
    """
    implements(IOnlineHelp, IContainmentRoot)

    def __init__(self, title, path):
        self._registry = {}
        super(OnlineHelp, self).__init__(title, path)

    def getTopicsForInterfaceAndView(self, interface, view=None):
        "See zope.app.onlinehelp.interfaces.IOnlineHelp"
        return self._registry.get((interface, view), [])

    def getTopicForObjectAndView(self, obj, view=None):
        "See zope.app.Onlinehelp.interfaces.IOnlineHelp"
        topic = self
        for iface in providedBy(obj):
            topics = self.getTopicsForInterfaceAndView(
                iface,
                view
                )
            if len(topics)>0:
                topic = topics[0]
                break
        return topic

    def registerHelpTopic(self, parent_path, id, title,
                          doc_path, interface=None, view=None,
                          resources=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        parent = zapi.traverse(self, parent_path)
        # Create and add topic
        parent[id] = OnlineHelpTopic(title, doc_path)
        topic = parent[id]

        # add resources to topic
        if resources is not None:
            topic.addResources(resources)

        # Add topic to registry
        if interface is not None:
            if not self._registry.has_key((interface, view)):
                self._registry[(interface, view)] = []
            self._registry[(interface, view)].append(topic)


