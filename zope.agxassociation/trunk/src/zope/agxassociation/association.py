##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Association support


$Id$
"""

from zope import schema, proxy
import zope.schema.interfaces # allow schema.interfaces to be used

class readproperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self

        return self.func(inst)

class Association(schema.Field):

    @readproperty
    def target(self):
        names = self.target_name.split('.')
        
        target_module = __import__('.'.join(names[:-1]), {}, {}, ['*'])
        self.target = getattr(target_module, names[-1])
        
        return self.target

    def __init__(self, target, inverse=None, cardinality=None, **kw):
        if isinstance(target, str):
            self.target_name = target
        else:
            self.target = target

        self.inverse = inverse

        if cardinality is None:
            cardinality = SINGLE
        self.cardinality = cardinality

        super(Association, self).__init__(**kw)

    def _validate(self, value):
        super(Association, self)._validate(value)
        if not self.target.providedBy(value):
            raise schema.interfaces.WrongType(self.target, value)

    def inverse_add(self, ob, value):
        """Add an inverse reference if the association has an inverse
        """
        if not self.inverse:
            return
        inverse = self.target[self.inverse]
        inverse.add(value, ob, self)
        
    def add(self, ob, value, inverse):
        """Add a forward reference to provide an inverse.

        They key is that we *don't add an inverse reference, as this has
        already been done.
        """
        self.cardinality.add(self, ob, value, inverse)

class SingleCardinality:

    def add(self, field, ob, value, inverse):
        try:
            old = field.get(ob)
        except AttributeError:
            # XXX need more direct way to test
            old = field.missing_value
            
        if old is value:
            # Nothing to do
            return

        if old != field.missing_value:
            # remove the old inverse ref
            inverse.remove(old, ob)

        field.set(ob, value)
            
SINGLE = SingleCardinality()

class Property(object):

    def __init__(self, field, name=None):
        self.field = field
        if name is None:
            name = field.__name__
        self.__name__ = name

class SingleProperty(Property):

    def __get__(self, inst, class_):
        if inst is None:
            return self

        try:
            return inst.__dict__[self.__name__]
        except KeyError:
            raise AttributeError(self.__name__)

    def __set__(self, inst, value):
        self.field.validate(value)
        old = inst.__dict__.get(self.__name__, self.field.missing_value)
        if old != self.field.missing_value:
            self.field.inverse_remove(ob, old)
        inst.__dict__[self.__name__] = value
        self.field.inverse_add(inst, value)

    def __delete__(self, inst):
        old = inst.__dict__.get(self.__name__, self)
        if old is self:
            raise AttributeError(self.__name__)
        if old != self.field.missing_value:
            self.field.inverse_remove(ob, old)
        del inst.__dict__[self.__name__]
        

class SetCardinality:

    def add(self, field, ob, value, inverse):
        set = field.get(ob)
        set.add(value)


class SetProxy(proxy.ProxyBase):

    __slots__ = 'inst', 'field'

    def add(self, x):
        set = proxy.getProxiedObject(self)
        if x in set:
            return
        self.field.validate(x)
        set.add(x)
        self.field.inverse_add(self.inst, x)

class SetProperty(Property):

    def __get__(self, inst, class_):
        if inst is None:
            return self

        set = inst.__dict__.get(self.__name__)
        if set is None:
            raise AttributeError(self.__name__)

        set = SetProxy(set)
        set.inst = inst
        set.field = self.field

        return set

    def __set__(self, inst, set):
        inst.__dict__[self.__name__] = set

    def __delete__(self, inst):
        del inst.__dict__[self.__name__]



