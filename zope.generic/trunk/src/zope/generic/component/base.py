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
from persistent import IPersistent
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
from zope.generic.component import IKeyface
from zope.generic.component import IAttributeKeyface
from zope.generic.component import IKeyfaceDescription
from zope.generic.component import adapter
from zope.generic.component.helper import toDottedName



class Keyface(object):
    """Key interface mixin for key interface attribute implementations.
    
    You can mixin this class if you like to provide IKeyface for
    IAttributeKeyface implementations:

        >>> class AnyAttributeKeyface(Keyface):
        ...    def __init__(self, keyface):
        ...         self.__keyface__ = keyface

        >>> fake_keyface = object()
        >>> any = AnyAttributeKeyface(fake_keyface)
        >>> any.__keyface__ == fake_keyface
        True

    You get only the following method decorator for free :):

        >>> any.keyface == fake_keyface
        True
            
    """

    implements(IKeyface)

    @property
    def keyface(self):
        return self.__keyface__



class KeyfaceDescription(Keyface):
    """Key interface description mixin."""

    implements(IKeyfaceDescription)

    def __init__(self, keyface, label=None, hint=None):
        self.__keyface__ = keyface

        if label is None:
            self.label = _(keyface.__name__)
        else:
            self.label = label

        if hint is None:
            self.hint = _(keyface.__doc__)
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

    The implementation provide an adapter to IKeyface by its __conform__
    method:

        >>> adapted = IKeyface(config_data)
        >>> IKeyface.providedBy(adapted)
        True

        >>> adapted.keyface is IBarConfiguration
        True

        
    """

    implements(IAttributeKeyface, IConfigurationData)

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
        self.__dict__['__keyface__'] = schema
        directlyProvides(self, schema)

    def __conform__(self, keyface):
        if keyface is IKeyface:
            return adapter.Keyface(self)

    def __getattr__(self, name):
        # assert IAttributeKeyface
        if name == '__keyface__':
            return self.__dict__['__keyface__']

        schema = self.__dict__['__keyface__']
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
        schema = self.__dict__['__keyface__']
        data = self.__dict__['_ConfigurationData__data']

        if not(name == '__provides__' or name in IPersistent):
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



class InformationProvider(KeyfaceDescription):
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

        >>> info.keyface == IFooMarker
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

    def __init__(self, keyface, provides, label=None, hint=None):
        super(InformationProvider, self).__init__(keyface, label, hint)
        alsoProvides(self, provides)