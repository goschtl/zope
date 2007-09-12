##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Standard mapper class.

$Id$
"""

from types import DictType

import interfaces
from interfaces import ConfigurationError


class Mapper:
    """Standard mapper class.
    """
    __implements__ = interfaces.IConfigurableMapper
    name = None
    class_name = None
    serializer = None
    gateway = None
    initializers = None

    def __init__(self, name=None, class_name=None,
                 serializer=None, gateway=None):
        self.name = name
        self.class_name = class_name
        self.serializer = serializer
        self.gateway = gateway
        self.initializers = []

    # IConfigurableMapper implementation

    def check(self, my_name):
        s = self.serializer
        if s is None:
            raise ConfigurationError(
                'Mapper %s: No serializer configured' % my_name)
        if not interfaces.IFullObjectSerializer.isImplementedBy(s):
            raise ConfigurationError(
                'Mapper %s: Serializer is not an IFullObjectSerializer'
                % my_name)
        g = self.gateway
        if g is None:
            raise ConfigurationError(
                'Mapper %s: No gateway configured' % my_name)
        if not interfaces.IGateway.isImplementedBy(g):
            raise ConfigurationError(
                'Mapper %s: Gateway is not an IGateway' % my_name)
        if s.schema != g.schema:
            # Try to show a descriptive error
            ss = s.schema
            gs = g.schema
            text = None
            if isinstance(ss, DictType) and isinstance(gs, DictType):
                for key in ss.keys():
                    if not gs.has_key(key):
                        text = 'No gateway provided for serializer "%s"' % key
                        break
                    elif ss[key] != gs[key]:
                        text = 'Mismatch on name "%s". %s != %s' % (
                            key, ss[key], gs[key])
                        break
                if text is None:
                    for key in gs.keys():
                        if not ss.has_key(key):
                            text = ('No serializer provided for gateway "%s"'
                                   % key)
                            break
            if text is None:
                text = '%s != %s' % (ss, gs)
            raise ConfigurationError(
                'Mapper %s: Mismatched schemas. %s' % (my_name, text))


class MapperConfiguration:
    """Collects the mapper configuration with a classifier and OID generator.
    """
    __implements__ = interfaces.IMapperConfiguration
    mappers = None
    classifier = None
    oid_gen = None
    initializers = None

    def __init__(self, mappers, classifier, oid_gen):
        self.mappers = mappers
        self.classifier = classifier
        self.oid_gen = oid_gen
        self.initializers = []

    def check(self):
        for name, mapper in self.mappers.items():
            mapper.check(name)
