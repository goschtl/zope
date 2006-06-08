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

from persistent import IPersistent
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList

from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema import ValidationError
from zope.schema.interfaces import IField

from zope.generic.face import IAttributeFaced
from zope.generic.face import IFace
from zope.generic.face import IUndefinedContext
from zope.generic.face.api import FaceForAttributeFaced
from zope.generic.face.api import toDottedName

from zope.generic.configuration import IConfigurationData
from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import INestedConfiguration
from zope.generic.configuration.field import ISubConfiguration
from zope.generic.configuration.field import ISubConfigurationDict
from zope.generic.configuration.field import ISubConfigurationList



def createConfiguration(keyface, data):
    """Factory function for configuration data."""

    return ConfigurationData(keyface, data)



def createConfigurationList(field, data):

    if ISubConfiguration.providedBy(field.value_type):
        subkeyface = field.value_type.schema
        counter = 0
        subconfigurations = []
        while data:
            subdata = subData(str(counter), data)
            if subdata:
                subconfigurations.append(createConfiguration(subkeyface, subdata))
            else:
                raise IndexError('list index out of range')

            counter += 1
            
        return ConfigurationList(subconfigurations)

    # other objects
    else:
        indices = data.keys()
        indices.sort()
        # precondition: assume that everythings is ok if the start and end point is ok
        if int(indices[0]) != 0 or int(indices[-1]) != len(indices) - 1:
            raise IndexError('list index out of range')
        return ConfigurationList([data[index] for index in indices])



def createConfigurationDict(field, data):
    if ISubConfiguration.providedBy(field.value_type):
        subkeyface = field.value_type.schema
        subconfigurations = {}
        while data:
            prefix = iter(data).next().split('.')[0] # evaluate the next entry  
            subconfigurations[prefix] = createConfiguration(subkeyface, subData(prefix, data))

        return ConfigurationDict(subconfigurations)

    # other objects
    else:
        return ConfigurationDict(data)



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
    relevant_data = {}
    for name in __keyface__:
        # forget missing but none-required
        if name not in data:
            field = __keyface__[name]
            # handle nested configuration data
            if INestedConfiguration.providedBy(field):
                subdata = subData(name, data)

                if subdata or field.required is True:
                    if ISubConfiguration.providedBy(field):
                        relevant_data[name] = createConfiguration(field.schema, subdata)
                    elif ISubConfigurationList.providedBy(field):
                        relevant_data[name] = createConfigurationList(field, subdata)
                    elif ISubConfigurationDict.providedBy(field):
                        relevant_data[name] = createConfigurationDict(field, subdata)
                    else:
                        raise NotImplementedError()

                    continue

            if field.required is True:
                missedArguments.append(name)

        else:
            value = data[name]
            if isinstance(value, list):
                relevant_data[name] = ConfigurationList(value)

            elif isinstance(value, dict):
                relevant_data[name] = ConfigurationDict(value)
           
            else:
                relevant_data[name] = data[name]
    
    if missedArguments:
        raise TypeError("__init__ requires '%s' of '%s'." % (', '.join(missedArguments), __keyface__.__name__))
    
    return relevant_data



class ConfigurationList(PersistentList):
    """List-like configurations."""



class ConfigurationDict(PersistentDict):
    """Dict-like configurations."""



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
        
        >>> class IExampleConfiugration(Interface):
        ...    foo = TextLine(title=u'Foo')
        ...    fuu = TextLine(title=u'Fuu', required=False)
        ...    fii = TextLine(title=u'Fii', required=False, readonly=True)

    Create a corresponding configuration data:

        >>> config_data = ConfigurationData(IExampleConfiugration, {'foo': u'Foo!'})
        >>> config_data
        <Configuration zope.generic.configuration.base.IExampleConfiugration>

        >>> IExampleConfiugration.providedBy(config_data)
        True
        >>> config_data.foo
        u'Foo!'
        >>> config_data.fuu
        
        >>> config_data.bar
        Traceback (most recent call last):
        ...
        AttributeError: 'IExampleConfiugration' configuration has no attribute 'bar'.
 
    The implementation provide an adapter to IFace by its __conform__ method:

        >>> adapted = IFace(config_data)
        >>> IFace.providedBy(adapted)
        True

        >>> adapted.keyface is IExampleConfiugration
        True

    A configuration belong to the configuration context:

        >>> adapted.conface is IUndefinedContext
        True
 
    Readonly attribute can be set once. Afterward an value error is raised:

        >>> config_data.fii = u'Bla bla'
        >>> config_data.fii = u'Bla bla'
        Traceback (most recent call last):
        ...
        ValueError: 'IExampleConfiugration' configuration's attribute 'fii' is readonly.

    If a relevant key is missed within the data a key error is raised:

        >>> config_data = ConfigurationData(IExampleConfiugration, {})
        Traceback (most recent call last):
        ...
        TypeError: __init__ requires 'foo' of 'IExampleConfiugration'.

    The schema should never contain methods:

        >>> class IBarConfiguration(Interface):
        ...    bar = TextLine(title=u'Bar')
        ...    def method(self):
        ...        pass

        >>> config_data = ConfigurationData(IBarConfiguration, {'bar': u'Bar!', 'method': u'Method!'})
        Traceback (most recent call last):
        ...
        AttributeError: 'Method' object has no attribute 'readonly'

    """

    implements(IAttributeFaced, IConfigurationData)

    def __init__(self, __keyface__, data):
        # essentials
        self.__dict__['__keyface__'] = __keyface__
        self.__dict__['__conface__'] = IUndefinedContext
        directlyProvides(self, __keyface__)

        # set other data
        for key, value in prepareData(__keyface__, data).items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Configuration %s>' % toDottedName(self.__keyface__)

    def __conform__(self, interface):
        if interface is IFace:
            return FaceForAttributeFaced(self)

    def __getattr__(self, name):
        """Get value of a configuration."""

        # assert acces attribute faced attributes
        if name in ['__keyface__', '__conface__']:
            return self.__dict__[name]
        
        # filter all names except keyface attributes  
        else:
            # short cut
            data = self.__dict__
            keyface = data['__keyface__']

            try:
                field = keyface[name]
    
            except KeyError:
                raise AttributeError("'%s' configuration has no attribute '%s'." % (keyface.__name__, name))
    
            else:
                value = data.get(name, _marker)
                if value is _marker:
                    value = getattr(field, 'default', _marker)
                    if value is _marker:
                        # should not happen
                        raise RuntimeError("'%s' configuration's value for '%s' is missing." % (keyface.__name__, name))
        
                return value
        
            raise AttributeError("'%s' configuration has no attribute '%s'." % (keyface.__name__, name))


    def __setattr__(self, name, value):
        """Set value of a configuration."""

        # assert setting of dedicated  faced attributes
        if name == '__provides__' or name in IPersistent:
            super(ConfigurationData, self).__setattr__(name, value)
 
        else:
            # short cut
            data = self.__dict__
            keyface = data['__keyface__']

            try:
                field = keyface[name]
            except KeyError:
                raise AttributeError(name)
            else:
                if field.readonly and data.has_key(name):
                    raise ValueError("'%s' configuration's attribute '%s' is readonly." % (keyface.__name__, name))

                field = field.bind(self)
                try:
                    field.validate(value)
                    
                except ValidationError, e:
                    raise e.__class__("'%s' configuration's attribute '%s' is not valid: %s." % (keyface.__name__, name, ', '.join([repr(a) for a in e.args])))

                super(ConfigurationData, self).__setattr__(name, value)
