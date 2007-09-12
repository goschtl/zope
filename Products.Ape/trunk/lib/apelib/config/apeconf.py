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
"""Ape configuration assembler.

$Id$
"""
from __future__ import nested_scopes
from types import TupleType

from apelib.core.mapper import Mapper, MapperConfiguration
from apelib.core.serializers import CompositeSerializer
from apelib.core.gateways import CompositeGateway
from apelib.core.interfaces import IDatabaseInitializer, ConfigurationError

from apelib.zodb3.zodbtables import Table, TableSchema
from common import Directive, DirectiveReader, ComponentSystem


class MapperDefinition(Directive):
    schema = TableSchema()
    schema.add('mapper_name', primary=1)
    schema.add('extends')
    schema.add('class_name')


class ComponentDefinition(Directive):
    schema = TableSchema()
    # comptypes: 'classifier', 'oid_generator'
    schema.add('comptype', primary=1)
    schema.add('name', primary=1)
    schema.add('producer')


class MapperComponent(Directive):
    schema = TableSchema()
    schema.add('mapper_name', primary=1)
    # comptypes: 'serializer', 'gateway'
    schema.add('comptype', primary=1)
    schema.add('name', primary=1)
    schema.add('producer')
    schema.add('order')


class StoreUsing(Directive):
    schema = TableSchema()
    schema.add('class_name', primary=1)
    schema.add('use_mapper')
    schema.add('exact')  # boolean
    schema.add('default_extension')
    schema.add('default_extension_source')


class LoadUsing(Directive):
    schema = TableSchema()
    # Criterion is 'extension', 'mapper-name', or 'generic'
    schema.add('criterion', primary=1)
    schema.add('value', primary=1)
    schema.add('use_mapper')


class DisabledProducer:
    def __init__(self, source):
        self.source = source

    def __call__(self, compsys):
        return None


class FactoryProducer:

    def __init__(self, source, factory):
        self.source = source
        pos = factory.find('(')
        if pos >= 0:
            # Arguments specified.  Interpret as a Python expression.
            args = eval(factory[pos:])
            if not isinstance(args, TupleType):
                args = (args,)
            factory = factory[:pos]
        else:
            args = ()
        pos = factory.rfind('.')
        if pos <= 0:
            raise ValueError, "Module and class name required"
        self.module_name = factory[:pos]
        self.class_name = factory[pos + 1:]
        self.args = args
        self.sub_producer = None

    def __call__(self, compsys):
        params = []
        if self.args:
            params.extend(self.args)
        if self.sub_producer is not None:
            obj = self.sub_producer(compsys)
            params.append(obj)
        m = __import__(self.module_name, {}, {}, ('__doc__',))
        try:
            c = getattr(m, self.class_name)
        except AttributeError:
            raise ImportError, "No class %s in module %s" % (
                self.class_name, self.module_name)
        return c(*params)


def make_producer(source, comptype, attrs, raise_exc=1):
    if attrs.get('enabled', '').lower() == 'false':
        return DisabledProducer(source)
    elif attrs.has_key('factory'):
        return FactoryProducer(source, attrs['factory'])
    elif raise_exc:
        raise ValueError, "Need a 'factory' or 'enabled' attribute"
    else:
        return None


def get_element_handlers():
    """Returns a dictionary of XML element handlers.
    """

    def handle_configuration(source, vars, attrs):
        assert vars.has_key('directives')

    def handle_variation(source, vars, attrs):
        variations = vars['variations']
        name = attrs['name']
        d = variations.get(name)
        if d is None:
            # Make a new variation.
            d = []
            variations[name] = d
        vars['directives'] = d

    def handle_mapper(source, vars, attrs):
        d = vars['directives']
        mapper_name = str(attrs['name'])
        extends = str(attrs.get('extends', ''))
        class_name = str(attrs.get('class', ''))
        vars['mapper_name'] = mapper_name
        d.append(MapperDefinition(source, mapper_name, extends, class_name))

    def handle_mapper_component(source, vars, attrs, comptype):
        d = vars['directives']
        producer = make_producer(source, comptype, attrs)
        mapper_name = vars.get('mapper_name')
        if mapper_name is None:
            raise ValueError('Not inside a mapper tag')
        else:
            # Composite component of a mapper
            name = attrs.get('name', '')
            directive = MapperComponent(
                source, mapper_name, comptype,
                name, producer, attrs.get('order', 'middle'))
        d.append(directive)
        return producer

    def handle_serializer(source, vars, attrs):
        handle_mapper_component(source, vars, attrs, 'serializer')

    def handle_gateway(source, vars, attrs):
        p = vars.get('classifier_producer')
        if p is not None:
            # Set a gateway for a classifier.
            if not hasattr(p, 'sub_producer'):
                raise ValueError(
                    "Classifier at %s needs a factory" % source)
            if p.sub_producer is not None:
                raise ValueError(
                    "Multiple gateways in classifiers not allowed at %s" %
                    source)
            p.sub_producer = make_producer(source, 'gateway', attrs)
        else:
            handle_mapper_component(source, vars, attrs, 'gateway')

    def handle_classifier(source, vars, attrs):
        d = vars['directives']
        producer = make_producer(source, 'classifier', attrs)
        directive = ComponentDefinition(source, 'classifier', '', producer)
        d.append(directive)
        vars['classifier_producer'] = producer

    def handle_oid_generator(source, vars, attrs):
        d = vars['directives']
        producer = make_producer(source, 'oid_generator', attrs)
        directive = ComponentDefinition(source, 'oid_generator', '', producer)
        d.append(directive)

    def handle_store(source, vars, attrs):
        d = vars['directives']
        cn = attrs.get('class')
        ecn = attrs.get('exact-class')
        if cn and ecn or not cn and not ecn:
            raise ValueError("One of 'class' or 'exact-class' is required")
        mapper_name = str(attrs['using'])
        def_ext = attrs.get('default-extension')
        def_ext_src = attrs.get('default-extension-source')
        if def_ext and def_ext_src:
            raise ValueError(
                "Only one of 'default-extension' "
                "or 'default-extension-source' is allowed")
        directive = StoreUsing(
            source, cn or ecn, mapper_name, bool(ecn), def_ext, def_ext_src)
        d.append(directive)

    def handle_load(source, vars, attrs):
        d = vars['directives']
        mapper_name = str(attrs['using'])
        criterion = None
        for attr in ('mapper-name', 'extensions', 'generic'):
            if attrs.has_key(attr):
                if criterion is not None:
                    raise ValueError("Only one criterion allowed")
                criterion = attr
                v = attrs[attr]
                if attr == 'extensions':
                    first = 1
                    for ext in v.split():
                        if not ext.startswith('.'):
                            ext = '.' + ext
                        ext = ext.lower()
                        d.append(LoadUsing(
                            source, 'extension', ext, mapper_name))
                else:
                    d.append(LoadUsing(
                        source, attr, v, mapper_name))

    handlers = {
        'configuration': handle_configuration,
        'variation':     handle_variation,
        'mapper':        handle_mapper,
        'serializer':    handle_serializer,
        'gateway':       handle_gateway,
        'classifier':    handle_classifier,
        'oid-generator': handle_oid_generator,
        'store':        handle_store,
        'load':       handle_load,
        }

    return handlers



class BasicComponentAssembler:
    """Assembler for producer-based components.

    Configures at the time of creation.
    """

    def __init__(self, compsys, comptype, name):
        self.compsys = compsys
        records = compsys.dtables.query(
            ComponentDefinition, comptype=comptype, name=name)
        if not records:
            raise ConfigurationError("No %s component named %s exists"
                                     % (comptype, repr(name)))
        assert len(records) == 1
        producer = records[0]['producer']
        self.producer = producer

    def create(self):
        self.obj = self.producer(self.compsys)
        return self.obj

    def configure(self):
        pass


class MapperAssembler:
    """Assembler for one mapper component.
    """
    def __init__(self, compsys, comptype, name):
        self.compsys = compsys
        dtables = compsys.dtables
        self.mapper_name = name
        recs = dtables.query(MapperDefinition, mapper_name=name)
        if not recs:
            raise ConfigurationError("No mapper named %s exists" % repr(name))
        self.directive = recs[0]
        self.subobjs = []  # all subobjects
        self._prepare_sub_components()

    def _prepare_sub_components(self):
        """Populates multi_comps with components to be used in this mapper.
        """
        self.multi_comps = {}  # comptype -> name -> record
        dtables = self.compsys.dtables
        name = self.mapper_name
        all_names = []  # mapper_name and all of its base mapper_names
        while name:
            all_names.append(name)
            records = dtables.query(
                MapperComponent, mapper_name=name)
            for r in records:
                d = self.multi_comps.setdefault(r.comptype, {})
                d.setdefault(r.name, r)
            name = dtables.query_field(
                MapperDefinition, 'extends', mapper_name=name)
            if name and name in all_names:
                raise ConfigurationError(
                    "Circular extension in mappers %s" % repr(all_names))

    def create(self):
        self.obj = Mapper()
        return self.obj

    def configure(self):
        self.obj.name = self.mapper_name
        self.obj.class_name = self.directive.class_name or ''
        self.add_serializers()
        self.add_gateways()
        self.add_initializers()

    def add_serializers(self):
        d = self.multi_comps.get('serializer', {})

        # Create the main serializer
        r = d.get('')
        if r:
            s = r.producer(self.compsys)
        else:
            s = CompositeSerializer()

        # Create the contained serializers
        ordered = [
            ((r.order or '').lower(), name, r)
            for name, r in d.items() if name]
        ordered.sort()
        for order, name, r in ordered:
            o = r.producer(self.compsys)
            if o is not None:
                s.add(str(name), o)
                self.subobjs.append(o)

        # Assign it
        self.obj.serializer = s

    def add_gateways(self):
        d = self.multi_comps.get('gateway', {})

        # Create the main gateway
        r = d.get('')
        if r:
            g = r.producer(self.compsys)
        else:
            g = CompositeGateway()

        # Create the contained gateways
        for name, r in d.items():
            if name:
                o = r.producer(self.compsys)
                if o is not None:
                    g.add(str(name), o)
                    self.subobjs.append(o)

        # Assign it
        self.obj.gateway = g

    def add_initializers(self):
        for o in self.subobjs:
            if IDatabaseInitializer.isImplementedBy(o):
                self.obj.initializers.append(o)


class ClassifierAssembler (BasicComponentAssembler):
    """Assembler for one classifier.
    """
    def __init__(self, compsys, comptype, name):
        assert comptype == "classifier", comptype
        assert name == '', name
        BasicComponentAssembler.__init__(self, compsys, comptype, name)

    def configure(self):
        dtables = self.compsys.dtables
        for r in dtables.query(StoreUsing):
            self.obj.add_store_rule(
                r.class_name, r.use_mapper, r.exact,
                r.default_extension, r.default_extension_source)
        for r in dtables.query(LoadUsing):
            self.obj.add_load_rule(r.criterion, r.value, r.use_mapper)


def configure(filenames, vname=''):
    """Returns a MapperConfiguration built from configuration files.
    """
    handlers = get_element_handlers()
    reader = DirectiveReader(handlers)
    for fn in filenames:
        reader.read(fn)
    directives = reader.get_directives(vname)
    cs = ComponentSystem(directives)
    cs.add_component_type('mapper', MapperAssembler)
    cs.add_component_type('classifier', ClassifierAssembler)
    cs.add_component_type('oid_generator', BasicComponentAssembler)
    mappers = {}
    for record in cs.dtables.query(MapperDefinition):
        name = record.mapper_name
        mappers[name] = cs.get('mapper', name)
    classifier = cs.get('classifier', '')
    oid_gen = cs.get('oid_generator', '')
    conf = MapperConfiguration(mappers, classifier, oid_gen)
    for obj in (classifier.gateway, oid_gen):
        if IDatabaseInitializer.isImplementedBy(obj):
            conf.initializers.append(obj)
    conf.check()
    return conf

