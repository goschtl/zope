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
"""Handle code: directives

$Id: metaconfigure.py,v 1.2 2003/08/21 14:19:24 srichter Exp $
"""
from zope.app.interpreter import provideInterpreter

def registerInterpreter(_context, type, component):
    return _context.action(
        discriminator = ('code', 'registerInterpreter', type),
        callable = provideInterpreter,
        args = (type, component)
        )
