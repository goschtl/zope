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
"""
$Id$
"""

def hook(_context, name, implementation, module=None):
    if module:
        name = "%s.%s" % (module, name)
    hook = _context.resolve(name)
    sethook = getattr(hook, 'sethook', None)
    if sethook is None:
        raise TypeError(name,'is not hookable')
    implementation = _context.resolve(implementation)
    _context.action(
        discriminator=('http://namespaces.zope.org/zope/hook', name),
        callable=sethook,
        args=(implementation, )
        )
