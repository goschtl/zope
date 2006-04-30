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

from zope.location import Location
from zope.interface import classImplements
from zope.interface import implements

from zope.generic.configuration import IConfiguration
from zope.generic.configuration import IConfigurations

from zope.generic.adapter.property import ConfigurationAdapterProperty



class ConfigurationAdapterBase(Location):
    """Base mixin for simple configuration adapter."""

    __keyface__ = None

    def __init__(self, context):
        self.__context__ = context
        self.__configurations__ = IConfigurations(context)



def ConfigurationAdapterClass(keyface, informationProviders=None, bases=()):
    """Generic configuration adapter class factory.

    The generic configuration adapter is a generic adapter class for 
    instances providing configurations. First we declare a configuration
    schema:

        >>> from zope.schema import TextLine

        >>> class IFooConfiguration(interface.Interface):
        ...    foo = TextLine(title=u'Foo', required=False, default=u'Default config.')

    We register the configuration schema using generic:face directive:

        >>> registerDirective('''
        ... <generic:face
        ...     keyface="example.IFooConfiguration"
        ...     type="zope.generic.configuration.IConfiguration"
        ...     />
        ... ''') 

        >>> from zope.generic.configuration import IConfiguration
        >>> IConfiguration.providedBy(IFooConfiguration)
        True

    We implement a class which is providing the configuration mechanism:
    
        >>> class IFoo(interface.Interface):
        ...    pass

        >>> registerDirective('''
        ... <generic:face
        ...     keyface="example.IFoo"
        ...     />
        ... ''')

        >>> from zope.generic.configuration import IAttributeConfigurable

        >>> class Foo(object):
        ...     interface.implements(IFoo, IAttributeConfigurable)

        >>> foo = Foo()

        >>> from zope.generic.configuration.api import queryConfiguration

        >>> queryConfiguration(foo, IFooConfiguration) is None
        True

    The simple configuration adapter function will construct an adapter class
    implementing the IFooConfiguration interface:

        >>> from zope.generic.adapter.adapter import ConfigurationAdapterClass
        
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

        >>> queryConfiguration(foo, IFooConfiguration).foo
        u'Foo config.'

        >>> adapted.foo = u'Another foo value.'
        >>> adapted.foo
        u'Another foo value.'

    """

    # preconditions
    if not IConfiguration.providedBy(keyface):
        raise ValueError('Interface must provide %s.' % IConfiguration.__name__)

    # essentails
    if not bases:
        bases = (ConfigurationAdapterBase, )

    class_ = type('ConfigurationAdapterClass from %s' % keyface, bases,
                  {'__keyface__': keyface})

    classImplements(class_, keyface)

    # add field properties for each object field
    for name in keyface:
        field = keyface[name]
        setattr(class_, name, ConfigurationAdapterProperty(keyface[name], providers=informationProviders))

    return class_
