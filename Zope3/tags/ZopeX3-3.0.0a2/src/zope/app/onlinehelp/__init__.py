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

from zope.app.onlinehelp.interfaces import IOnlineHelpTopic, IOnlineHelp
from zope.interface import implements

class OnlineHelpTopic(SampleContainer):
    """
    Represents a Help Topic.
    
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> path = os.path.join(testdir(), 'help.txt')

    Create a Help Topic from a file
    
    >>> topic = OnlineHelpTopic('Help',path)

    Test the title
    
    >>> topic.title
    'Help'

    The type should be set to plaintext, since
    the file extension is 'txt'
    
    >>> topic.type
    'zope.source.plaintext'

    Test the help content.

    >>> topic.source
    'This is a help!'

    >>> path = os.path.join(testdir(), 'help.stx')
    >>> topic = OnlineHelpTopic('Help',path)

    The type should now be structured text
    >>> topic.type
    'zope.source.stx'

    HTML files are treated as structured text files
    >>> path = os.path.join(testdir(), 'help.html')
    >>> topic = OnlineHelpTopic('Help',path)

    The type should still be structured text
    >>> topic.type
    'zope.source.stx'

    >>> path = os.path.join(testdir(), 'help.rst')
    >>> topic = OnlineHelpTopic('Help',path)

    The type should now be restructured text
    >>> topic.type
    'zope.source.rest'

    """
    implements(IOnlineHelpTopic)

    title = u""

    source = None

    path = u""

    type = None

    def __init__(self, title, path):
        """Initialize object."""
        self.title = title
        self.path = path

        filename = os.path.basename(path.lower())
        file_ext = 'txt'
        if len(filename.split('.'))>1:
            file_ext = filename.split('.')[-1]

        self.type = 'zope.source.plaintext'
        
        if file_ext in ('rst', 'rest') :
            self.type = 'zope.source.rest'
        elif file_ext == 'stx':
            self.type = 'zope.source.stx'
        elif file_ext in ('html', 'htm'):
            self.type = 'zope.source.stx'
        
        self.source = open(self.path).read()

        super(OnlineHelpTopic, self).__init__()


class OnlineHelp(OnlineHelpTopic):
    """
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import testdir
    >>> from zope.app.onlinehelp.tests.test_onlinehelp import I1
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
    
    """
    implements(IOnlineHelp, IContainmentRoot)

    def __init__(self, title, path):
        self._registry = {}
        super(OnlineHelp, self).__init__(title, path)

    def getTopicsForInterfaceAndView(self, interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        return self._registry.get((interface, view), [])

    def registerHelpTopic(self, parent_path, id, title,
                          doc_path, interface=None, view=None):
        "See Zope.App.OnlineHelp.interfaces.IOnlineHelp"
        parent = zapi.traverse(self, parent_path)
        # Create and add topic
        parent[id] = OnlineHelpTopic(title, doc_path)
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
