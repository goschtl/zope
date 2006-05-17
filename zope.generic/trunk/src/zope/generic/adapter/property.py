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

from zope.generic.configuration import IConfigurations
from zope.generic.configuration.base import createConfiguration
from zope.generic.configuration.helper import configuratonToDict
from zope.generic.informationprovider.api import getInformation
from zope.generic.informationprovider.api import getInformationProvider



_marker = object()

class ConfigurationAdapterProperty(object):
    """Compute configuration adapter attributes based on schema fields

    Field properties provide default values, data validation and error messages
    based on data found in field meta-data.

    Note that ConfigurationAdapterProperty cannot be used with slots. 
    They can only be used for attributes stored in instance configurations
    dictionaries.
    """

    def __init__(self, field, name=None, providers=None):
        if name is None:
            name = field.__name__

        self._field = field
        self._name = name
        self._providers = providers

    def __get__(self, inst, klass):
        if inst is None:
            return self

        # assume attribute configurables
        try:
            configurations = inst.__configurations__

        # try to adapt
        except:
            configurations = IConfigurations(inst)

        keyface = inst.__keyface__
        context = inst.__context__

        # evaluate configuration
        configuration = inst.__keyface__(configurations, None)
        # Try to evaluate configuration from information provider
        if configuration is None and self._providers:
            for registry in self._providers:
                try:
                    provider = getInformationProvider(context, registry)
                    configuration = getInformation(keyface, provider)
                    break
                except:
                    pass

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

        # assume attribute configurables
        try:
            configurations = inst.__configurations__

        # try to adapt
        except:
            configurations = IConfigurations(inst)

        keyface = inst.__keyface__
        # update existing configuration
        if keyface in configurations:
            configurations.update(keyface, {self._name: value})
            
        # create a new configuration
        else:
            try:
                configurations[keyface] = createConfiguration(keyface, {self._name: value})

            except TypeError, e:
                # hack around the atomic update of the form framework
                # try to invoke acquire settings
                context = inst.__context__
                configuration = None
                if configuration is None and self._providers:
                    for registry in self._providers:
                        try:
                            provider = getInformationProvider(context, registry)
                            configuration = getInformation(keyface, provider)
                            break
                        except:
                            pass

                # no information available
                if not configuration:
                    raise

                data = configuratonToDict(configuration)
                data[self._name] = value
                configurations[keyface] = createConfiguration(keyface, data)

        inst.__dict__[self._name] = value

    def __getattr__(self, name):
        return getattr(self._field, name)
