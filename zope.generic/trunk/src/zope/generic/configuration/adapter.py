##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from BTrees.OOBTree import OOBTree
import transaction
from UserDict import DictMixin

from zope.app.location import Location
from zope.app.location.interfaces import ILocation
from zope.component import adapts
from zope.event import notify
from zope.interface import classImplements
from zope.interface import implements

from zope.generic.keyface import IAttributeKeyfaced
from zope.generic.keyface.api import toDottedName
from zope.generic.keyface.api import toKeyface

from zope.generic.configuration import IAttributeConfigurable
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations
from zope.generic.configuration.base import ConfigurationData
from zope.generic.configuration.event import Configuration
from zope.generic.configuration.event import ObjectConfiguredEvent
from zope.generic.configuration.helper import configuratonToDict



class AttributeConfigurations(DictMixin, Location):
    """Store configurations on an object within the __configurations__ attribute.

    """

    implements(IConfigurations)

    adapts(IAttributeConfigurable)

    def __init__(self, context):
        self.context = context

    def __nonzero__(self):
        return bool(getattr(self.context, '__configurations__', 0))

    def __conform__(self, keyface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return None

        else:
            return configurations.get(toDottedName(keyface), None)

    def __getitem__(self, keyface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            raise KeyError(keyface)

        return configurations[toDottedName(keyface)]

    def keys(self):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return []

        return [toKeyface(iface) for iface in configurations.keys()]

    def update(self, keyface, data):
        current_config = self[keyface]

        updated_data = {}
        errors = []
        
        savepoint = transaction.savepoint()
        try:
            for name, value in data.items():
                # raise attribute error
                field = keyface[name]
                if field.readonly:
                    raise ValueError(name, 'Data is readonly.')
                else:
                    if value != getattr(current_config, name, field.missing_value):
                        setattr(current_config, name, value)
                        updated_data[name] = value

            # notify update
            parent = self.__parent__
            if updated_data and ILocation.providedBy(parent) and parent.__parent__ is not None:
                notify(ObjectConfiguredEvent(parent, 
                    Configuration(keyface, updated_data)))

        except:
            savepoint.rollback()
            raise

    def __setitem__(self, keyface, value):
        # preconditions
        if not IConfigurationType.providedBy(keyface):
            raise KeyError('Interface key %s does not provide %s.' % 
                (keyface.__name__, IConfigurationType.__name__))

        if not keyface.providedBy(value):
            raise ValueError('Value does not provide %s.' % keyface.__name__)

        # essentials
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            configurations = self.context.__configurations__ = OOBTree()

        data = configuratonToDict(keyface, value, all=True)
        configurations[toDottedName(keyface)] = value
        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            notify(ObjectConfiguredEvent(parent, 
                Configuration(keyface, data)))

    def __delitem__(self, keyface):
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            raise KeyError(keyface)

        del configurations[toDottedName(keyface)]
        # notify deletion
        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            notify(ObjectConfiguredEvent(parent, 
                Configuration(keyface, {})))



_marker = object()

class ConfigurationAdapterProperty(object):
    """Compute configuration adapter attributes based on schema fields

    Field properties provide default values, data validation and error messages
    based on data found in field meta-data.

    Note that ConfigurationAdapterProperty cannot be used with slots. 
    They can only be used for attributes stored in instance configurations
    dictionaries.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self._field = field
        self._name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configurations = inst.__configurations__
        keyface = inst.__keyface__
        context = inst.__context__

        # evaluate configuration
        configuration = inst.__keyface__(configurations, None)
        value = getattr(configuration, self._name, _marker)
        if value is _marker:
            field = self._field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self._name)

        return value

    def __set__(self, inst, value):
        field = self._field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self._name, 'field is readonly')

        configurations = inst.__configurations__
        keyface = inst.__keyface__
        # update existing configuration
        if keyface in configurations:
            configurations.update(keyface, {self.__name: value})
            
        # create a new configuration
        else:
            configurations[keyface] = ConfigurationData(keyface, {self._name: value})

        inst.__dict__[self._name] = value

    def __getattr__(self, name):
        return getattr(self._field, name)



class ConfigurationAdapterBase(Location):
    """Base mixin for simple configuration adapter."""

    __keyface__ = None

    def __init__(self, context):
        self.__context__ = context
        self.__configurations__ = IConfigurations(context)



def ConfigurationAdapterClass(keyface, bases=(), property=None):
    """Generic configuration adapter class factory.

    The generic configuration adapter is a generic adapter class for 
    instances providing configurations. First we declare a configuration
    schema:

        >>> from zope.schema import TextLine

        >>> class IFooConfiguration(interface.Interface):
        ...    foo = TextLine(title=u'Foo', required=False, default=u'Default config.')

    We register the configuration schema using generic:keyface directive:

        >>> registerDirective('''
        ... <generic:keyface
        ...     keyface="example.IFooConfiguration"
        ...     type="zope.generic.configuration.IConfigurationType"
        ...     />
        ... ''') 

        >>> from zope.generic.configuration import IConfigurationType
        >>> IConfigurationType.providedBy(IFooConfiguration)
        True

    We implement a class which is providing the configuration mechanism:
    
        >>> class IFoo(interface.Interface):
        ...    pass

        >>> registerDirective('''
        ... <generic:keyface
        ...     keyface="example.IFoo"
        ...     />
        ... ''')

        >>> class Foo(object):
        ...     interface.implements(IFoo, api.IAttributeConfigurable)

        >>> foo = Foo()

        >>> api.queryConfiguration(foo, IFooConfiguration) is None
        True

    The simple configuration adapter function will construct an adapter class
    implementing the IFooConfiguration interface:

        >>> from zope.generic.configuration.adapter import ConfigurationAdapterClass
        
        >>> FooConfigurationAdapter = ConfigurationAdapterClass(IFooConfiguration)
        >>> IFooConfiguration.implementedBy(FooConfigurationAdapter)
        True

    We can adapt our foo to IFooConfiguration:

        >>> adapted = FooConfigurationAdapter(foo)
        >>> IFooConfiguration.providedBy(adapted)
        True
        >>> adapted.foo
        u'Default config.'

        >>> adapted.foo = u'Foo config.'
        >>> adapted.foo
        u'Foo config.'

        >>> api.queryConfiguration(foo, IFooConfiguration).foo
        u'Foo config.'

    """

    # preconditions
    if not IConfigurationType.providedBy(keyface):
        raise ValueError('Interface must provide %s.' % IConfigurationType.__name__)

    # essentails
    if not bases:
        bases = (ConfigurationAdapterBase, )

    class_ = type('ConfigurationAdapterClass from %s' % keyface, bases,
                  {'__keyface__': keyface})

    classImplements(class_, keyface)
    
    if property is None:
        property = ConfigurationAdapterProperty

    # add field properties for each object field
    for name in keyface:
        field = keyface[name]
        setattr(class_, name, property(keyface[name]))

    return class_
