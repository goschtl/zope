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

$Id: fields.py,v 1.2 2003/07/29 16:29:01 jim Exp $
"""

import os
from zope import schema
from zope.schema.interfaces import IFromUnicode
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements

class GlobalObject(schema.Field):
    """An object that can be accesses as a module global

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

    implements(IFromUnicode)

    def __init__(self, value_type=None, **kw):
        self.value_type = value_type
        super(GlobalObject, self).__init__(**kw)

    def _validate(self, value):
        super(GlobalObject, self)._validate(value)
        if self.value_type is not None:
            self.value_type.validate(value)

    def fromUnicode(self, u):
        name = str(u.strip())
        try:
            value = self.context.resolve(name)
        except ConfigurationError, v:
            raise schema.ValidationError(v)
            
        self.validate(value)
        return value

class Tokens(schema.Sequence):
    """A sequence that can be read from a spece-separated string

    Consider GlobalObject tokens:

    Examples:

    First, we need to set up a stub name resolver:

    >>> d = {'x': 1, 'y': 42, 'z': 'zope', 'x.y.x': 'foo'}
    >>> class fakeresolver(dict):
    ...     def resolve(self, n):
    ...         return self[n]

    >>> fake = fakeresolver(d)


    >>> g = Tokens(value_type=GlobalObject())
    >>> gg = g.bind(fake)
    >>> gg.fromUnicode("  \\n  x y z  \\n")
    [1, 42, 'zope']

    >>> g = Tokens(value_type=
    ...            GlobalObject(value_type=
    ...                         schema.Int(constraint=lambda x: x%2 == 0)))
    >>> gg = g.bind(fake)
    >>> gg.fromUnicode("x y")
    Traceback (most recent call last):
    ...
    ValidationError: Invalid token: (u'Constraint not satisfied', 1) in x y

    >>> gg.fromUnicode("z y")
    Traceback (most recent call last):
    ...
    ValidationError: Invalid token: (u'Wrong type', 'zope', """ \
                             """(<type 'int'>, <type 'long'>)) in z y
    >>> gg.fromUnicode("y y")
    [42, 42]
    >>> 

    """

    implements(IFromUnicode)

    def fromUnicode(self, u):
        u = u.strip()
        if u:
            vt = self.value_type.bind(self.context)
            values = []
            for s in u.split():
                try:
                    v = vt.fromUnicode(s)
                except schema.ValidationError, v:
                    raise schema.ValidationError("Invalid token: %s in %s"
                                                 % (v, u))
                else:
                    values.append(v)
        else:
            values = []
            
        self.validate(values)

        return values

class Path(schema.Text):
    """A file path name, which may be input as a relative path

    Input paths are converted to absolute paths and normalized.

    Let's look at an example:

    First, we need a "context" for the field that has a path
    function for converting relative path to an absolute path.

    We'll be careful to do this in an os-independent fashion.

    >>> class FauxContext:
    ...    def path(self, p):
    ...       return os.path.join(os.sep, 'faux', 'context', p)
    
    >>> context = FauxContext()
    >>> field = Path().bind(context)

    Lets try an absolute path first:

    >>> p = unicode(os.path.join(os.sep, 'a', 'b'))
    >>> n = field.fromUnicode(p)
    >>> n.split(os.sep)
    [u'', u'a', u'b']

    Now try a relative path:

    >>> p = unicode(os.path.join('a', 'b'))
    >>> n = field.fromUnicode(p)
    >>> n.split(os.sep)
    [u'', u'faux', u'context', u'a', u'b']
    

    """

    implements(IFromUnicode)

    def fromUnicode(self, u):
        if os.path.isabs(u):
            return os.path.normpath(u)
        
        return self.context.path(u)

class Bool(schema.Bool):
    """A boolean value

    Values may be input (in upper or lower case) as any of:
       yes, no, y, n, true, false, t, or f.

    >>> Bool().fromUnicode(u"yes")
    1
    >>> Bool().fromUnicode(u"y")
    1
    >>> Bool().fromUnicode(u"true")
    1
    >>> Bool().fromUnicode(u"no")
    0
    """

    implements(IFromUnicode)

    def fromUnicode(self, u):
        u = u.lower()
        if u in ('1', 'true', 'yes', 't', 'y'):
            return True
        if u in ('0', 'false', 'no', 'f', 'n'):
            return False
        raise schema.ValidationError

class MessageID(schema.Text):
    """Text string that should be translated.

    When a string is converted to a message ID, it is also
    recorded in the context.

    >>> class FauxContext:
    ...     i18n_strings = {} 

    >>> context = FauxContext()
    >>> field = MessageID().bind(context)

    We can't do anything if we don't have a domain:

    >>> i = field.fromUnicode("Hello world!")
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify a an i18n translation domain

    With the domain specified:

    >>> context.domain = 'testing'

    We can get a message id:

    >>> i = field.fromUnicode(u"Hello world!")
    >>> i
    u'Hello world!'
    >>> i.domain
    'testing'

    In addition, the string has been registered with the context:

    >>> context.i18n_strings
    {'testing': {u'Hello world!': 1}}

    >>> i = field.fromUnicode(u"Foo Bar")
    >>> i = field.fromUnicode(u"Hello world!")
    >>> context.i18n_strings
    {'testing': {u'Foo Bar': 1, u'Hello world!': 1}}
    """

    implements(IFromUnicode)

    __factories = {}

    def fromUnicode(self, u):
        domain = getattr(self.context, 'domain', '')
        if not domain:
            raise ConfigurationError(
                "You must specify a an i18n translation domain")
        v = super(MessageID, self).fromUnicode(u)

        # Record the string we got for the domain
        i18n_strings = self.context.i18n_strings
        strings = i18n_strings.get(domain)
        if strings is None:
            strings = i18n_strings[domain] = {}
        strings[v] = 1

        # Convert to a message id, importing the factory, if necessary
        factory = self.__factories.get(domain)
        if factory is None:
            import zope.i18n.messageid
            factory = zope.i18n.messageid.MessageIDFactory(domain)
            self.__factories[domain] = factory

        return factory(v)
