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
"""OnlineHelp System.

Create the global OnlineHelp instance. 

$Id$
"""
import os

import zope
from zope.app import zapi
from onlinehelp import OnlineHelp
from onlinehelptopic import OnlineHelpTopic
from zope.app.onlinehelp.interfaces import IOnlineHelp    


class helpNamespace:
    """ help namespace handler """

    def __init__(self, context, request=None):
        self.context = context

    def traverse(self, name, ignored):
        """Used to traverse to an online help topic."""
        onlinehelp = zapi.getUtility(IOnlineHelp,
                                          'OnlineHelp', self.context)
        onlinehelp.context = self.context
        return onlinehelp

# Global Online Help
path = os.path.join(os.path.dirname(zope.app.__file__),
                    'onlinehelp', 'help','welcome.stx')

help = OnlineHelp('Online Help', path)
