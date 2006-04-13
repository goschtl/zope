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

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField

from zope.generic.component import IAttributeConfigurable
from zope.generic.component import IConfigurationData
from zope.generic.component import IConfigurations
from zope.generic.component import IInformationProvider
from zope.generic.component import IKeyInterface
from zope.generic.component import IAttributeKeyInterface
from zope.generic.component import IKeyInterfaceDescription
from zope.generic.component import adapter
from zope.generic.component.helper import toDottedName



class KeyInterface(object):
    """Key interface mixin for key interface attribute implementations.
    
    You can mixin this class if you like to provide IKeyInterface for
    IAttributeKeyInterface implementations:

        >>> class AnyAttributeKeyInterface(KeyInterface):
        ...    def __init__(self, key):
        ...         self.__key_interface__ = key

        >>> fake_key_interface = object()
        >>> any = AnyAttributeKeyInterface(fake_key_interface)
        >>> any.__key_interface__ == fake_key_interface
        True

    You get only the following method decorator for free :):

        >>> any.key == fake_key_interface
        True
            
    """

    implements(IKeyInterface)

    @property
    def key(self):
        return self.__key_interface__



class KeyInterfaceDescription(KeyInterface):
    """Key interface description mixin."""

    implements(IKeyInterfaceDescription)

    def __init__(self, key, label=None, hint=None):
        self.__key_interface__ = key

        if label is None:
            self.label = _(key.__name__)
        else:
            self.label = label

        if hint is None:
            self.hint = _(key.__doc__)
        else:
            self.hint = hint



_marker = object()

class ConfigurationData(Persistent):
    """Generic configuration data.
    
    The generic configuration data implementation can be used to create
    instances providing a certain configuration schema on the fly. This is done
    only by a __getattr__ and a __setattr__ method that asserts the configuration
    schema constraint.

    We first have to define an example configuration schema:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IExampleConfiugrationSchema(Interface):
        ...    foo = TextLine(title=u'Foo')
        ...    fuu = TextLine(title=u'Fuu', required=False)
        ...    fii = TextLine(title=u'Fii', required=False, readonly=True)

    Create a corresponding configuration data:

        >>> config_data = ConfigurationData(IExampleConfiugrationSchema, {'foo': u'Foo!'})
        >>> IExampleConfiugrationSchema.providedBy(config_data)
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

        >>> config_data = ConfigurationData(IExampleConfiugrationSchema, {})
        Traceback (most recent call last):
        ...
        AttributeError: 'IExampleConfiugrationSchema' object has no attribute 'foo'.

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

    The implementation provide an adapter to IKeyInterface by its __conform__
    method:

        >>> adapted = IKeyInterface(config_data)
        >>> IKeyInterface.providedBy(adapted)
        True

        >>> adapted.key is IBarConfiguration
        True

        
    """

    implements(IAttributeKeyInterface, IConfigurationData)

    def __init__(self, schema, data):
        # preconditions
        missedArguments = []
        for name in schema:
            if name not in data:
                field = schema[name]
                if field.required is True:
                    missedArguments.append(name)
        
        if missedArguments:
            raise AttributeError("'%s' object has no attribute '%s'." % (schema.__name__, ', '.join(missedArguments)))
    
        # essentials
        self.__dict__['_ConfigurationData__data'] = PersistentDict(data)
        self.__dict__['__key_interface__'] = schema
        directlyProvides(self, schema)

    def __conform__(self, interface):
        if interface is IKeyInterface:
            return adapter.KeyInterface(self)

    def __getattr__(self, name):
        # assert IAttributeKeyInterface
        if name == '__key_interface__':
            return self.__dict__['__key_interface__']

        schema = self.__dict__['__key_interface__']
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
            #setattr(self, name, v)
            return v
        raise AttributeError(name)

    def __setattr__(self, name, value):
        schema = self.__dict__['__key_interface__']
        data = self.__dict__['_ConfigurationData__data']

        if name != '__provides__':
            try:
                field = schema[name]
            except KeyError:
                raise AttributeError(name)
            else:
                if field.readonly is True:
                    raise ValueError(name, 'Data is readonly.')
            data[name] = value
        else:
            super(ConfigurationData, self).__setattr__(name, value)



class InformationProvider(KeyInterfaceDescription, dict):
    """Generic information provider.

    Information do relate a dedicated type of information marked as an interface
    extending IInformationProvider and another marker interface:

        >>> class ISpecialInformation(IInformationProvider):
        ...    pass

        >>> from zope.interface import Interface
        >>> class IFooMarker(Interface):
        ...    '''Foo is member of the example domain.'''

        >>> info = InformationProvider(IFooMarker, ISpecialInformation)

    The information will provide the interface of the dedicated information:

        >>> ISpecialInformation.providedBy(info)
        True

    The information is related to the interface declared by the interface
    attribute:

        >>> info.key == IFooMarker
        True
        >>> info.label
        u'IFooMarker'
        
        >>> info.hint
        u'Foo is member of the example domain.'


    Often you will provide a specific label and hint for the end-user:

        >>> info = InformationProvider(IFooMarker, ISpecialInformation, u'Foo', u'Bla bla.')
        >>> info.label
        u'Foo'
        
        >>> info.hint
        u'Bla bla.'
    """

    implements(IInformationProvider, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, key, provides, label=None, hint=None):
        super(InformationProvider, self).__init__(key, label, hint)
        alsoProvides(self, provides)