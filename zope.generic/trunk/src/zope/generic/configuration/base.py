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

from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.interfaces import IObject
from zope.schema.interfaces import IContainer

from zope.generic.face import IAttributeFaced
from zope.generic.face import IFace
from zope.generic.face import IUndefinedContext
from zope.generic.face.api import FaceForAttributeFaced

from zope.generic.configuration import IConfigurationData
from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration.helper import getValue



def subData(name, data):
    """Return a subdata dict and remove the subdata from the given data dict.

    Example 1:

        >>> data = {'x.y': 2, 'x.a': 3, 'x.': 4, 'xa': 5}
        >>> subData('x', data)
        {'y': 2, 'a': 3}
    """

    subdata = {}

    prefix = name + '.'
    prefix_len = len(name + '.')

    # add subdata to dictionary
    for key, value in data.items():
        if len(key) > prefix_len and key.startswith(prefix):
            subdata[key[prefix_len:]] = value
            del data[key]

    return subdata



def prepareData(__keyface__, data):
    """Nested configuration support."""
    missedArguments = []
    for name in __keyface__:
        # forget missing but none-required
        if name not in data:
            field = __keyface__[name]
            # handle nested configuration data
            if IObject.providedBy(field) and IConfigurationType.providedBy(field.schema):
                try:
                    subdata = subData(name, data)
                    if subdata or field.required is True:
                        data[name] = ConfigurationData(field.schema, subData(name, data))
                        break

                except:
                    pass

            if field.required is True:
                missedArguments.append(name)
    
    if missedArguments:
        raise TypeError("__init__ requires '%s' of '%s'." % (', '.join(missedArguments), __keyface__.__name__))
    
    return data
    


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
        TypeError: __init__ requires 'foo' of 'IExampleConfiugrationSchema'.

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

    The implementation provide an adapter to IFace by its __conform__
    method:

        >>> adapted = IFace(config_data)
        >>> IFace.providedBy(adapted)
        True

        >>> adapted.keyface is IBarConfiguration
        True

    A configuration belong to the configuration context:

        >>> adapted.conface is IUndefinedContext
        True

    """

    implements(IAttributeFaced, IConfigurationData)

    def __init__(self, __keyface__, data):
        # essentials
        self.__dict__['_ConfigurationData__data'] = PersistentDict(prepareData(__keyface__, data))
        self.__dict__['__keyface__'] = __keyface__
        self.__dict__['__conface__'] = IUndefinedContext
        directlyProvides(self, __keyface__)

    def __conform__(self, interface):
        if interface is IFace:
            return FaceForAttributeFaced(self)

    def __getattr__(self, name):
        # assert IAttributeFaced
        if name in ['__keyface__', '__conface__']:
            return self.__dict__[name]

        keyface = self.__dict__['__keyface__']
        data = self.__dict__['_ConfigurationData__data']

        return getValue(keyface, name, data)


    def __setattr__(self, name, value):

        if not(name == '__provides__' or name in IPersistent):
            keyface = self.__dict__['__keyface__']
            data = self.__dict__['_ConfigurationData__data']

            try:
                field = keyface[name]
            except KeyError:
                raise AttributeError(name)
            else:
                if field.readonly is True:
                    raise ValueError(name, 'Data is readonly.')
            data[name] = value
        else:
            super(ConfigurationData, self).__setattr__(name, value)
