##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Security related configuration fields.

$Id: fields.py,v 1.2 2004/04/11 10:34:41 srichter Exp $
"""
from zope import schema
from zope.interface import implements
from zope.schema.interfaces import IFromUnicode
from zope.app.security.permission import checkPermission

class Permission(schema.Id):
    r"""This field describes a permission.

    Let's look at an example:

    >>> class FauxContext:
    ...     permission_mapping = {'zope.ManageCode':'zope.private'}
    ...     _actions = []
    ...     def action(self, **kws):
    ...        self._actions.append(kws)
    >>> context = FauxContext()
    >>> field = Permission().bind(context)

    Let's test the fromUnicode method:

    >>> field.fromUnicode(u'zope.foo')
    'zope.foo'
    >>> field.fromUnicode(u'zope.ManageCode')
    'zope.private'

    Now let's see whether validation works alright

    >>> field._validate('zope.ManageCode')
    >>> context._actions[0]['args']
    (None, 'zope.foo')
    >>> field._validate('3 foo')
    Traceback (most recent call last):
    ...
    InvalidId: 3 foo

    zope.Public is always valid
    >>> field._validate('zope.Public')
    """
    implements(IFromUnicode)

    def fromUnicode(self, u):
        u = super(Permission, self).fromUnicode(u)

        map = getattr(self.context, 'permission_mapping', {})
        return map.get(u, u)

    def _validate(self, value):
        super(Permission, self)._validate(value)

        if value != 'zope.Public':
            self.context.action(
                discriminator = None,
                callable = checkPermission,
                args = (None, value)
                )
        
