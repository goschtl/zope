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
"""Interfaces related to context wrappers.

$Id: context.py,v 1.1 2003/06/01 17:22:10 jim Exp $
"""

from zope.interface import Interface

class IContextWrapper(Interface):
    """Wrapper API provided to applications."""

    def ContextWrapper(object, parent, **data):
        """Create a context wrapper for object in parent

        If the object is in a security proxy, then result will be
        a security proxy for the unproxied object in context.

        Consider an object, o1, in a proxy p1 with a checker c1.

        If we call ContextWrapper(p1, parent, name='foo'), then we'll
        get::

          Proxy(Wrapper(o1, parent, name='foo'), c1)
        """
