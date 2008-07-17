from zope import interface
from zope import schema
from zope import component

from zope.dottedname.resolve import resolve
from zope.security.interfaces import IChecker
from zope.security.checker import defineChecker, getCheckerForInstancesOf
from zope.security.proxy import removeSecurityProxy

from interfaces import IMapper
from interfaces import IMapped

import sqlalchemy as rdb
from sqlalchemy import orm

from sqlalchemy.orm.attributes import proxied_attribute_factory

from z3c.saconfig import Session

from uuid import uuid1
from random import randint
from itertools import chain

import bootstrap
import soup
import zs2sa
import types

def decode(name):
    return resolve(name.replace(':', '.'))

def encode(iface):
    return iface.__identifier__.replace('.', ':')

def expand(iface):
    yield iface

    for spec in iface.getBases():
        for iface in expand(spec):
            yield iface

@interface.implementer(IMapper)
@component.adapter(interface.Interface)
def getMapper(spec):
    """Return a mapper for the specification."""
    if not callable(spec):
        raise TypeError("Create called for non-factory", spec)

    if IMapped.providedBy(spec):
        return spec.__mapper__

    return createMapper(spec)

def createMapper(spec):
    """Create a mapper for the specification."""

    engine = Session().bind
    metadata = engine.metadata

    exclude = ['__name__']

    # expand specification
    if interface.interfaces.IInterface.providedBy(spec):
        ifaces = set([spec.get(name).interface for name in spec.names(True)])
        kls = object
    else:
        implemented = interface.implementedBy(spec)
        fields = chain(*[schema.getFields(iface) for iface in implemented])
        ifaces = set([implemented.get(name).interface for name in fields])
        kls = spec

        for name, value in spec.__dict__.items():
            if isinstance(value, property):
                exclude.append(name)

    assert ifaces, "Specification must declare at least one field."
    
    # create joined table
    properties = {}
    first_table = None
    
    for (t, p) in (getTable(iface, metadata, exclude) for iface in ifaces):
        if first_table is None:
            table = first_table = t
        else:
            table = table.join(t, onclause=(t.c.id==first_table.c.id))
        properties.update(p)

    specification_path = '%s.%s' % (spec.__module__, spec.__name__)

    class Mapper(bootstrap.Soup, kls):
        interface.implements(IMapped, *ifaces)

        __spec__ = specification_path
        
        def __init__(self, *args, **kwargs):
            super(Mapper, self).__init__(*args, **kwargs)

            # set soup metadata
            self.uuid = "{%s}" % uuid1()
            self.spec = self.__spec__

    # if the specification is an interface class, try to look up a
    # security checker and define it on the mapper
    if interface.interfaces.IInterface.providedBy(spec):
        checker = component.queryAdapter(spec, IChecker)
    # if not, assign the checker from the specification to the mapper.
    else:
        checker = getCheckerForInstancesOf(spec)

    if checker is not None:
        defineChecker(Mapper, checker)

    # set class representation method if not defined
    if not isinstance(Mapper.__repr__, types.MethodType):
        def __repr__(self):
            return "<Mapper (%s.%s) at %s>" % \
                   (spec.__module__, spec.__name__, hex(id(self)))

        Mapper.__repr__ = __repr__

    # set ``property``-derived properties directly on the mapper
    for name, prop in properties.items():
        if isinstance(prop, property):
            del properties[name]
            setattr(Mapper, name, prop)

    soup_table = bootstrap.Soup.c.id.table
    polymorphic = (
        [Mapper], table.join(
        soup_table, first_table.c.id==soup_table.c.id))

    orm.mapper(
        Mapper,
        table,
        properties=properties,
        exclude_properties=exclude,
        with_polymorphic=polymorphic,
        inherits=bootstrap.Soup,
        inherit_condition=(first_table.c.id==soup_table.c.id))

    spec.__mapper__ = Mapper
    interface.alsoProvides(spec, IMapped)

    return Mapper

def removeMapper(spec):
    del spec.mapper
    interface.noLongerProvides(spec, IMapped)

        
def getTable(iface, metadata, ignore=()):
    name = encode(iface)

    columns = []
    properties = {}
    
    for field in map(lambda key: iface[key], iface.names()):
        property_factory = None

        if field.__name__ in ignore:
            continue

        try:
            factories = zs2sa.fieldmap[type(field)]
        except KeyError:
            # raise NotImplementedError("Field type unsupported (%s)." % field)
            continue

        try:
            column_factory, property_factory = factories
        except TypeError:
            column_factory = factories
            
        if column_factory is not None:
            column = column_factory(field, metadata)
            columns.append(column)
        else:
            column = None
            
        if property_factory is not None:
            props = property_factory(field, column, metadata)
            properties.update(props)

    if name in metadata.tables:
        return metadata.tables[name], properties
        
    kw = dict(useexisting=True)

    table = rdb.Table(
        name,
        metadata,
        rdb.Column('id', rdb.Integer, rdb.ForeignKey(bootstrap.Soup.c.id), primary_key=True),
        *columns,
        **kw)

    metadata.create_all(checkfirst=True)
    
    return table, properties
