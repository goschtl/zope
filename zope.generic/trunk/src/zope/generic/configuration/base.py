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

from persistent import Persistent
from persistent.dict import PersistentDict

from zope.app.annotation import IAnnotations
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField
from zope.schema.fieldproperty import FieldProperty

from zope.generic.configuration import IConfigurationHandler
from zope.generic.configuration import IConfigurations
from zope.generic.configuration import missing

__all__ = ['ConfigurationData']
_marker = object()



class ConfigurationData(Persistent):
    """Generic configuration data.

    Provide a configuration schema:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IFooConfiguration(Interface):
        ...    foo = TextLine(title=u'Foo')
        ...    fuu = TextLine(title=u'Fuu', required=False)
        ...    fii = TextLine(title=u'Fii', required=False, readonly=True)

    Create a corresponding configuration data:

        >>> config_data = ConfigurationData(IFooConfiguration, {'foo': u'Foo!'})
        >>> IFooConfiguration.providedBy(config_data)
        True
        >>> config_data.foo
        u'Foo!'
        >>> config_data.fuu
        
        >>> config_data.bar
        Traceback (most recent call last):
        ...
        AttributeError: bar
        
        >>> config_data.fii = u'Bla bla'
        Traceback (most recent call last):
        ...
        ValueError: ('fii', 'Data is readonly.')

    If a relevant key is missed within the data a key error is raised:

        >>> config_data = ConfigurationData(IFooConfiguration, {})
        Traceback (most recent call last):
        ...
        KeyError: 'Missed keys: foo.'

    The schema should not contain methods:

        >>> class IBarConfiguration(Interface):
        ...    bar = TextLine(title=u'Bar')
        ...    def method(self):
        ...        pass

        >>> config_data = ConfigurationData(IBarConfiguration, {'bar': u'Bar!', 'method': u'Method!'})
        >>> config_data.bar
        u'Bar!'
        >>> config_data.method
        Traceback (most recent call last):
        ...
        RuntimeError: ('Data value is not a schema field', 'method')
    """

    def __init__(self, schema, data):
        # preconditions
        missedKeys = []
        for name in schema:
            if name not in data:
                field = schema[name]
                if field.required is True:
                    missedKeys.append(name)
        
        if missedKeys:
            raise KeyError('Missed keys: %s.' % ', '.join(missedKeys))
    
        # essentials
        self.__dict__['_ConfigurationData__data'] = PersistentDict(data)
        self.__dict__['_ConfigurationData__schema'] = schema
        directlyProvides(self, schema)

    def __getattr__(self, name):
        schema = self.__dict__['_ConfigurationData__schema']
        data = self.__dict__['_ConfigurationData__data']
        try:
            field = schema[name]
        except KeyError:
            raise AttributeError(name)
        else:
            value = data.get(name, _marker)
            if value is _marker:
                value = getattr(field, 'default', _marker)
                if value is _marker:
                    raise RuntimeError('Data is missing', name)

            if IMethod.providedBy(field):
                if not IField.providedBy(field):
                    raise RuntimeError('Data value is not a schema field', name)
                v = lambda: value
            else:
                v = value
            # setattr(self, name, v)
            return v
        raise AttributeError(name)

    def __setattr__(self, name, value):
        schema = self.__dict__['_ConfigurationData__schema']
        data = self.__dict__['_ConfigurationData__data']

        if name != '__provides__':
            try:
                field = schema[name]
            except KeyError:
                raise AttributeError(name)
            else:
                if field.readonly is True:
                    raise ValueError(name, 'Data is readonly.')
            data['name'] = value
        else:
            super(ConfigurationData, self).__setattr__(name, value)



class ConfigurationHandler(object):
    """Configuration handler."""

    implements(IConfigurationHandler)

    interface = FieldProperty(IConfigurationHandler['interface'])
    passConfigurations = FieldProperty(IConfigurationHandler['passConfigurations'])
    passAnnotations = FieldProperty(IConfigurationHandler['passAnnotations'])

    def __init__(self, callable, interface=None, passConfigurations=False,
                 passAnnotations=False):

        self.__callable = callable

        # otherwise use IPrivatConfigurationHandler
        if interface is not None:
            self.interface = interface

        self.passAnnotations = passAnnotations
        self.passConfigurations = passConfigurations

    def __call__(self, component, event, configurations=None, annotations=None):
        if configurations is None and self.passConfigurations is True:
            configurations = IConfigurations(component, missing)

        if annotations is None and self.passAnnotations is True:
            annotations = IAnnotations(component, missing)

        self._apply(component, event, configurations, annotations)

    def _apply(self, component, event, configurations, annotations):
        # this method can be overwritten by subclasses
        if self.__callable is not None:
            return self.__callable(component, event, configurations, annotations)



class ConfigurationHandlerChain(ConfigurationHandler):
    """Process a chain of configuration handlers."""

    implements(IConfigurationHandler)

    interface = FieldProperty(IConfigurationHandler['interface'])

    def __init__(self, handlers, interface=None, passConfigurations=True,
                 passAnnotations=True):
        super(ConfigurationHandlerChain, self).__intit__(None, interface, passConfigurations, passAnnotations)
        self.__handlers = handlers

    def _apply(self, component, event, configurations, annotations):
        """Invoke handler in the listed order."""
        [handler(component, event, configurations, annotations) for handler in self.__handlers]
