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
"""Register security related configuration directives.

$Id: metaconfigure.py,v 1.5 2003/08/17 06:08:00 philikon Exp $
"""
from zope.security.manager import setSecurityPolicy

def securityPolicy(_context, component):

    if callable(component):
        component = component()

    _context.action(
            discriminator = 'defaultPolicy',
            callable = setSecurityPolicy,
            args = (component,) )
