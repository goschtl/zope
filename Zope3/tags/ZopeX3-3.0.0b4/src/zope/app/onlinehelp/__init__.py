##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""OnlineHelp System.

Create the global `OnlineHelp` instance. 

$Id$
"""
__docformat__ = 'restructuredtext'

import os

import zope
from zope.interface import providedBy
from zope.testing import cleanup
from zope.app import zapi

from interfaces import IOnlineHelpTopic
from onlinehelp import OnlineHelp


# Global Online Help Instance
path = os.path.join(os.path.dirname(zope.app.__file__),
                    'onlinehelp', 'help','welcome.stx')
help = OnlineHelp('Online Help', path)


class helpNamespace(object):
    """ help namespace handler """

    def __init__(self, context, request=None):
        self.context = context

    def traverse(self, name, ignored):
        """Used to traverse to an online help topic.
        Returns the global `OnlineHelp` instance with the traversal
        context.
        """
        help.context = self.context
        return help

def getTopicFor(obj, view=None):
    """Determine topic for an object and optionally a view.
    Iterate through all directly provided Interfaces and
    see if for the interface (and view) exists a Help Topic.

    Returns the first match.

    Prepare the tests:
    >>> import os
    >>> from tests.test_onlinehelp import testdir
    >>> from tests.test_onlinehelp import I1, Dummy1, Dummy2
    >>> path = os.path.join(testdir(), 'help.txt')

    Register a help topic for the interface 'I1' and the view 'view.html'
    >>> onlinehelp = OnlineHelp('Help', path)
    >>> path = os.path.join(testdir(), 'help2.txt')
    >>> onlinehelp.registerHelpTopic('', 'help2', 'Help 2',
    ...     path, I1, 'view.html')

    The query should return it ('Dummy1' implements 'I1):
    >>> getTopicFor(Dummy1(),'view.html').title
    'Help 2'

    A query without view should not return it
    >>> getTopicFor(Dummy1()) is None
    True

    Do the registration again, but without a view:
    >>> onlinehelp = OnlineHelp('Help', path)
    >>> onlinehelp.registerHelpTopic('', 'help2', 'Help 2',
    ...     path, I1, None)
    >>> getTopicFor(Dummy1()).title
    'Help 2'

    Query with view should not match
    >>> getTopicFor(Dummy1(), 'view.html') is None
    True

    Query with an object, that does not provide 'I1' should
    also return None
    >>> getTopicFor(Dummy2()) is None
    True

    """
    topic = None
    for interface in providedBy(obj):
        for t in zapi.getUtilitiesFor(IOnlineHelpTopic):
            if t[1].interface==interface and t[1].view==view:
                topic = t[1]
                break

    return topic


def _clear():
    global help
    help.__init__(help.title, help.path)


cleanup.addCleanUp(_clear)
