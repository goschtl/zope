##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Serialization test setup/teardown

$Id$
"""

import ZODB
from Persistence import PersistentMapping
from cPickle import dumps, loads

from apelib.core import classifiers, gateways
from apelib.core import mapper, oidgen, schemas, serializers

from apelib.zodb3.serializers import PersistentMappingSerializer
from apelib.zodb3.serializers import RemainingState, RollCall


class TestObject(PersistentMapping):
    strdata = ""


def add_mapper(conf, klass, mapper_name):
    """Adds a simple mapper to the configuration.
    """
    serializer = serializers.CompositeSerializer()
    gateway = gateways.RAMGateway(serializer.schema)
    class_name = '%s.%s' % (klass.__module__, klass.__name__)
    m = mapper.Mapper(mapper_name, class_name, serializer, gateway)
    conf.mappers[mapper_name] = m
    conf.classifier.add_store_rule(class_name, mapper_name)
    return m


class SerialTestBase:

    def setUp(self):
        schema = schemas.ColumnSchema("classification", "classification")
        cfr = classifiers.SimpleClassifier(gateways.RAMGateway(schema))
        oid_gen = oidgen.SerialOIDGenerator()
        self.conf = mapper.MapperConfiguration({}, cfr, oid_gen)

        m = add_mapper(self.conf, PersistentMapping, "pm")
        m.serializer.add("items", PersistentMappingSerializer())
        m.serializer.add("rollcall", RollCall())
        m.gateway.schema = m.serializer.schema

        m = add_mapper(self.conf, TestObject, "tm")
        m.serializer.add("items", PersistentMappingSerializer())
        m.serializer.add("remainder", RemainingState())
        m.gateway.schema = m.serializer.schema

        self.conf.check()
        self.conns = {}

    def tearDown(self):
        pass

