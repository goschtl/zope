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
"""Configuration handlers for 'dav' namespace.

$Id: metaconfigure.py,v 1.2 2003/08/02 17:26:12 srichter Exp $
"""
from zope.app.services.servicenames import DAVSchema
from zope.app.component.metaconfigure import handler

def interface(_context, for_, interface):
    _context.action(
          discriminator = ('dav', 'provideInterface', for_, interface),
          callable = handler,
          args = (DAVSchema, 'provideInterface', for_, interface) )

