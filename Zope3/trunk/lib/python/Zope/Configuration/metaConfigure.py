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
"""
$Id: metaConfigure.py,v 1.2 2002/06/10 23:29:24 jim Exp $
"""
from Action import Action
from HookRegistry import HookRegistry

# one could make hookRegistry a service and
# theoretically use it TTW, but that doesn't immediately seem like a
# great idea
hookRegistry = HookRegistry()

addHookable = hookRegistry.addHookable
addHook = hookRegistry.addHook

def provideHookable(_context, name, module=None):
    if module:
        name = "%s.%s" % (module, name)
    name = _context.getNormalizedName(name)
    return [
        Action(
            discriminator=('addHookable', name),
            callable=addHookable,
            args=(name,)
            )
        ]


def provideHook(_context, name, implementation, module=None):
    if module:
        name = "%s.%s" % (module, name)
    name = _context.getNormalizedName(name)
    implementation = _context.getNormalizedName(implementation)
    return [
        Action(
            discriminator=('addHook', name),
            callable=addHook,
            args=(name, implementation)
            )
        ]



