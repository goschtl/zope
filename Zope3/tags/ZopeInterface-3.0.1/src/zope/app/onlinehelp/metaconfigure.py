##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Meta-Configuration Handlers for "help" namespace.

These handlers process the `registerTopic()` directive of
the "help" ZCML namespace.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.onlinehelp import help

def register(_context, id, title, parent="", doc_path=None, for_=None,
             view=None, resources=None):
    """Register an `OnlineHelp` topic"""

    _context.action(
        discriminator = ('registerHelpTopic', parent, id),
        callable = help.registerHelpTopic,
        args = (parent, id, title, doc_path, for_, view, resources) )
