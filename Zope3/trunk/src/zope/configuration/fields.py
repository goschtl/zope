##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
"""Configuration-specific schema fields

$Id: fields.py,v 1.1 2003/07/28 22:22:39 jim Exp $
"""

from zope import schema
from zope.schema.interfaces import IFromUnicode
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements

class GlobalObject(schema.Field):
    """An object that can be accesses as a module global
    """

    implements(IFromUnicode)

    def __init__(self, value_type=None, **kw):
        self.value_type = value_type
        super(GlobalObject, self).__init__(**kw)

    def _validate(self, value):
        super(GlobalObject, self)._validate(value)
        if self.value_type is not None:
            self.value_type.validate(value)

    def fromUnicode(self, u):
        """

        Examples:

        First, we need to set up a stub name resolver:
        >>> d = {'x': 1, 'y': 42, 'z': 'zope'}
        >>> class fakeresolver(dict):
        ...     def resolve(self, n):
        ...         return self[n]

        >>> fake = fakeresolver(d)


        >>> g = GlobalObject(value_type=schema.Int())
        >>> gg = g.bind(fake)
        >>> gg.fromUnicode("x")
        1
        >>> gg.fromUnicode("   x  \\n  ")
        1
        >>> gg.fromUnicode("y")
        42
        >>> gg.fromUnicode("z")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Wrong type', 'zope', (<type 'int'>, <type 'long'>))

        >>> g = GlobalObject(constraint=lambda x: x%2 == 0)
        >>> gg = g.bind(fake)
        >>> gg.fromUnicode("x")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Constraint not satisfied', 1)
        >>> gg.fromUnicode("y")
        42
        >>> 

        """
        name = str(u.strip())
        try:
            value = self.context.resolve(name)
        except ConfigurationError, v:
            raise schema.ValidationError(v)
            
        self.validate(value)
        return value

class GlobalObjects(schema.Sequence):
    """A sequence of global objects
    """

    implements(IFromUnicode)

    def fromUnicode(self, u):
        """
        Examples:

        First, we need to set up a stub name resolver:
        >>> d = {'x': 1, 'y': 42, 'z': 'zope', 'x.y.x': 'foo'}
        >>> class fakeresolver(dict):
        ...     def resolve(self, n):
        ...         return self[n]

        >>> fake = fakeresolver(d)


        >>> g = GlobalObjects()
        >>> gg = g.bind(fake)
        >>> gg.fromUnicode("  \\n  x y z  \\n")
        [1, 42, 'zope']

        >>> g = GlobalObjects(value_type=
        ...                   schema.Int(constraint=lambda x: x%2 == 0))
        >>> gg = g.bind(fake)
        >>> gg.fromUnicode("x y")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Wrong contained type', """ \
                                    """[Constraint not satisfied 1])
        >>> gg.fromUnicode("z y")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Wrong contained type', """ \
                     """[Wrong type zope (<type 'int'>, <type 'long'>)])
        >>> gg.fromUnicode("y y")
        [42, 42]
        >>> 

        """
        values = [self.context.resolve(name)
                  for name in str(u.strip()).split()]
        self.validate(values)
        return values

class Bool(schema.Bool):

    implements(IFromUnicode)

    def fromUnicode(self, u):
        u = u.lower()
        if u in ('1', 'true', 'yes', 't', 'y'):
            return True
        if u in ('0', 'false', 'no', 'f', 'n'):
            return False
        raise schema.ValidationError
