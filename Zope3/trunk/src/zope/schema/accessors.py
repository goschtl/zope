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
#
##############################################################################
"""\
Field accessors
===============

Accessors are used to model methods used to access data defgined by fields.
Accessors are fields that work by decorating existing fields.

To define accessors in an interface, use the accessors function::

  class IMyInterface(Interface):

     getFoo, setFoo = accessors(Text(title=u'Foo', ...))

     getBar, = accessors(TextLine(title=u'Foo', readonly=True, ...)


Normally a read accessor and a write accessor are defined.  Only a
readaccessor is defined for read-only fields.

Read accessors function as access method sepcifications and as field
specifications.  Write accessors are solely method specifications.

$Id: accessors.py,v 1.2 2003/04/18 22:12:33 jim Exp $
"""



from __future__ import generators

from zope.interface import directlyProvides
from zope.interface.interface import Method

class FieldReadAccessor(Method):
    """Field read accessor
    """

    # A read field accessor is a method and a field.
    # A read accessor is a decorator of a field, using the given
    # fields proprtyoes to provide meta data.

    def __init__(self, field):
        self.field = field
        Method.__init__(self, '')
        self.__doc__ = 'get %s' % field.__doc__
        directlyProvides(self, field.__implements__, Method.__implements__)

    def getSignatureString(self):
        return '()'

    def getSignatureInfo(self):
        return {'positional': (),
                'required': (),
                'optional': (),
                'varargs': None,
                'kwargs': None,
                }

    def get(self, object):
        return getattr(object, self.__name__)()

    def query(self, object, default=None):
        return getattr(object, self.__name__)()

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields")
        getattr(object, self.writer.__name__)(value)

    def __getattr__(self, name):
        return getattr(self.field, name)

    def bind(self, object):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.field = self.field.bind(object)
        return clone

class FieldWriteAccessor(Method):

    def __init__(self, field):
        Method.__init__(self, '')
        self.field = field
        self.__doc__ = 'set %s' % field.__doc__

    def getSignatureString(self):
        return '(newvalue)'

    def getSignatureInfo(self):
        return {'positional': ('newvalue',),
                'required': ('newvalue',),
                'optional': (),
                'varargs': None,
                'kwargs': None,
                }

def accessors(field):
    reader = FieldReadAccessor(field)
    yield reader
    if not field.readonly:
        writer = FieldWriteAccessor(field)
        reader.writer = writer
        yield writer

    
