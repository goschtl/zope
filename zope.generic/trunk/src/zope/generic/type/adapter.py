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

from zope.app.location import Location
from zope.component import adapts
from zope.interface import classImplements
from zope.interface import implements

from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration.api import ConfigurationData
from zope.generic.keyface import IAttributeKeyfaced
from zope.generic.informationprovider.api import provideInformation

from zope.generic.type import IInitializer
from zope.generic.type import IInitializerConfiguration
from zope.generic.type import ITypeable
from zope.generic.type.api import queryTypeConfiguration



class Initializer(object):
    """Initialize an object."""

    implements(IInitializer)
    
    adapts(ITypeable)

    def __init__(self, context):
        self.context = context

    def __call__(self, *pos, **kws):
        config = queryTypeConfiguration(self.context, IInitializerConfiguration)
        if config:
            # store initialization data
            if config.keyface:
                provideInformation(self.context, config.keyface, kws)

            # invoke initialization handler

            if config.handler:
                config.handler(self.context, *pos, **kws)


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

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configurations = inst.__configurations__
        keyface = inst.__keyface__
        context = inst.__context__

        configuration = inst.__keyface__(configurations, None)
        if configuration is None:
            # Try to evaluate a type configuration
            configuration = queryTypeConfiguration(context, keyface)

        value = getattr(configuration, self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self.__name, 'field is readonly')

        configurations = inst.__configurations__
        keyface = inst.__keyface__
        # update existing configuration
        if keyface in configurations:
            configurations.update(keyface, {self.__name: value})
            
        # create a new configuration
        else:
            configurations[keyface] = ConfigurationData(keyface, {self.__name: value})

        inst.__dict__[self.__name] = value

    def __getattr__(self, name):
        return getattr(self.__field, name)



class ConfigurationAdapterBase(Location):
    """Base mixin for simple configuration adapter."""

    __keyface__ = None

    def __init__(self, context):
        self.__context__ = context
        self.__configurations__ = IConfigurations(context)



def ConfigurationAdapterClass(keyface, bases=()):
    """Generic configuration adapter class factory.

    The generic configuration adapter is a generic adapter class for 
    configurations based instances. First we declare a configuration
    schema:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine

        >>> class IFooConfiguration(Interface):
        ...    foo = TextLine(title=u'Foo')

    We register the configuration schema using generic:configuration directive:

        >>> registerDirective('''
        ... <generic:keyface
        ...     keyface="example.IFooConfiguration"
        ...     type="zope.generic.configuration.IConfigurationType"
        ...     />
        ... ''') 

        >>> from zope.generic.configuration import IConfigurationType
        >>> IConfigurationType.providedBy(IFooConfiguration)
        True

    We use a generic type including a default configuration for our example, too:

        >>> class IFoo(Interface):
        ...    pass

        >>>

        >>> from zope.generic.configuration.api import ConfigurationData

        >>> foo_configuration = ConfigurationData(IFooConfiguration, {'foo': u'Type Foo'})

        >>> registerDirective('''
        ... <generic:type
        ...     keyface="example.IFoo"
        ...        class='zope.generic.type.api.Object'
        ...     >
        ...    <configuration
        ...        keyface='example.IFooConfiguration'
        ...        data='example.foo_configuration'
        ...       />
        ... </generic:type>
        ... ''')

        >>> foo = api.createObject(IFoo)
        >>> IFoo.providedBy(foo)
        True
        >>> api.queryTypeConfiguration(foo, IFooConfiguration).foo
        u'Type Foo'

    At the moment the foo instance does not provide a foo configuration:

        >>> api.queryObjectConfiguration(foo, IFooConfiguration) is None
        True

    The simple configuration adapter function will construct an adapter class
    implementing the IFooConfiguration interface:

        >>> from zope.generic.type.adapter import ConfigurationAdapterClass
        
        >>> FooConfigurationAdapter = ConfigurationAdapterClass(IFooConfiguration)
        >>> IFooConfiguration.implementedBy(FooConfigurationAdapter)
        True

    We can adapt our foo to IFooConfiguration:

        >>> adapted = FooConfigurationAdapter(foo)
        >>> IFooConfiguration.providedBy(adapted)
        True
        >>> adapted.foo
        u'Type Foo'

        >>> adapted.foo = u'Object Foo.'
        >>> adapted.foo
        u'Object Foo.'

        >>> api.queryObjectConfiguration(foo, IFooConfiguration).foo
        u'Object Foo.'

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

    # add field properties for each object field
    for name in keyface:
        field = keyface[name]
        setattr(class_, name, ConfigurationAdapterProperty(keyface[name]))

        # security assertions
        # protectName(class_, name, 'zope.ManageSite')
        # protectSetAttribute(class_, name, 'zope.ManageSite')

    return class_

