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
"""Unauthorized Exception definition

$Id: unauthorized.py,v 1.9 2003/08/12 19:14:50 srichter Exp $
"""
from types import StringType
from zope.exceptions import ZopeError
from zope.exceptions import IZopeError
from zope.exceptions import ZopeMessageIDFactory as _
from zope.interface import implements


class IUnauthorized(IZopeError):
    pass

class Unauthorized(ZopeError):
    """Some user wasn't allowed to access a resource"""

    implements(IUnauthorized)

    def __init__(self, message=None, value=None, needed=None, name=None, **kw):
        """Possible signatures:

        Unauthorized()
        Unauthorized(message) # Note that message includes a space
        Unauthorized(name)
        Unauthorized(name, value)
        Unauthorized(name, value, needed)
        Unauthorized(message, value, needed, name)

        Where needed is a mapping objects with items represnting requirements
        (e.g. {'permission': 'add spam'}). Any extra keyword arguments
        provides are added to needed.
        """
        if name is None and (
            not isinstance(message, StringType) or len(message.split()) <= 1):
            # First arg is a name, not a message
            name = message
            message = None

        self.name = name
        self.message = message
        self.value = value

        if kw:
            if needed:
                needed.update(kw)
            else:
                needed = kw

        self.needed = needed

    def __str__(self):
        if self.message is not None:
            return _(self.message)
        if self.name is not None:
            msg = _("You are not allowed to access ${name} in this context")
            msg.mapping = {'name': self.name}
        elif self.value is not None:
            msg = _("You are not allowed to access ${name} in this context")
            msg.mapping = {'name': self.getValueName()}
        return _("You are not authorized")


    def getValueName(self):
        v = self.value
        vname = getattr(v, '__name__', None)
        if vname:
            return vname
        c = getattr(v, '__class__', type(v))
        c = getattr(c, '__name__', 'object')
        msg = _("a particular ${object}")
        msg.mapping = {'object': c}
