##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Meta-Configuration Handlers for "help" namespace.

These handlers process the registerTopic() and unregisterTopic() directives of
the "help" ZCML namespace.

$Id: metaconfigure.py,v 1.5 2003/08/02 11:19:21 srichter Exp $
"""
import os
from zope.app.onlinehelp import help
from zope.app.component.metaconfigure import resolveInterface

def register(_context, id, title, parent="", doc_path=None, for_=None,
             view=None):
    """Register an OnlineHelp topic"""

    # XXX This should be really autodetected.
    doc_type="txt"

    _context.action(
        discriminator = ('registerHelpTopic', parent, id),
        callable = help.registerHelpTopic,
        args = (parent, id, title, doc_path, doc_type, for_, view) )
