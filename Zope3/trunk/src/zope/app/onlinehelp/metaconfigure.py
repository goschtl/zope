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

$Id: metaconfigure.py,v 1.2 2003/04/09 20:51:32 philikon Exp $
"""
import os
from zope.app.onlinehelp import help
from zope.app.component.metaconfigure import resolveInterface
from zope.configuration.action import Action

def register(_context, id, title, parent="", doc_path=None, doc_type="txt",
             for_=None, view=None):
    """Register an OnlineHelp topic"""
    actions = []

    doc_path = _context.path(doc_path)
    doc_path = os.path.normpath(doc_path)
    if for_ is not None:
        for_ = resolveInterface(_context, for_)
    if view is not None:
        view = _context.resolve(view)

    return [
        Action(discriminator = ('registerHelpTopic', parent, title),
               callable = help.registerHelpTopic,
               args = (parent, id, title, doc_path, doc_type, for_, view) )
        ]


def unregister(_context, path):
    return [
        Action(discriminator = ('unregisterHelpTopic', path),
               callable = help.unregisterHelpTopic,
               args = (path,) )
        ]
