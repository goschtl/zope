from zope import interface
from zope import schema
from zope import component

from zope.dottedname.resolve import resolve
from zope.security.interfaces import IChecker
from zope.security.checker import defineChecker

from interfaces import IMapper
from interfaces import IMapped

import sqlalchemy as rdb
from sqlalchemy import orm

from sqlalchemy.orm.attributes import proxied_attribute_factory

from ore.alchemist.interfaces import IDatabaseEngine
from ore.alchemist import Session
from ore.alchemist.zs2sa import FieldTranslator
from ore.alchemist.zs2sa import StringTranslator

import bootstrap
import relations

import factory

from itertools import chain

import types

class RelationProperty(property):
    def __init__(self, field):
        self.field = field
        self.name = field.__name__+'_relation'
        property.__init__(self, self.get, self.set)

    def get(kls, instance):
        item = getattr(instance, kls.name)
        return relations.lookup(item.uuid)

    def set(kls, instance, value):
        if not IMapped.providedBy(value):
            value = relations.persist(value)

        setattr(instance, kls.name, value)
        
class RelationList(object):
    __emulates__ = None
    
    def __init__(self):
        self.data = []

    @property
    def adapter(self):
        return self._sa_adapter

    # orm collection support
    
    @orm.collections.collection.appender
    def _appender(self, item):
        self.data.append(item)
    
    @orm.collections.collection.iterator
    def _iterator(self):
        return iter(self.data)

    @orm.collections.collection.remover
    def _remover(self, item):
        self.data.remove(item)
        
    # python list api
    
    def append(self, item, _sa_initiator=None):
        # make sure item is mapped
        if not IMapped.providedBy(item):
            item = relations.persist(item)

        # fire append event
        self.adapter.fire_append_event(item, _sa_initiator)

        # set up relation
        relation = bootstrap.Relation()
        relation.target = item
        relation.order = len(self.data)

        # save to session
        session = Session()
        session.save(relation)

        # add relation to internal list
        self.data.append(relation)

    def remove(self, item, _sa_initiator=None):
        if IMapped.providedBy(item):
            uuid = item.uuid
        else:
            uuid = item._d_uuid

        for relation in self.data:
            if relation.right == uuid:
                # fire remove event on target
                target = relations.lookup(uuid, ignore_cache=True)
                self.adapter.fire_remove_event(target, _sa_initiator)

                # remove reference to relation
                self.data.remove(relation)

                # delete from database
                session = Session()
                session.delete(relation)

                return

        return ValueError("Not in list: %s" % item)
        
    def extend(self, items):
        map(self.append, items)

    def __iter__(self):
        return (relation.target for relation in iter(self.data))

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index].target
        
    def __setitem__(self, index, value):
        return NotImplementedError("Setting items at an index is not implemented.")

class ObjectTranslator(object):
    def __init__(self, column_type=None):
        self.column_type = column_type

    def __call__(self, field, metadata):
        return rdb.Column(
            field.__name__+'_uuid', rdb.String(length=32), nullable=False)

class ObjectProperty(object):
    """Object property.

    We're not checking type here, because we'll only be creating
    relations to items that are joined with the soup.
    """
    
    def __call__(self, field, column, metadata):
        relation = RelationProperty(field)

        return {
            field.__name__: relation,
            relation.name: orm.relation(
            bootstrap.Soup,
            primaryjoin=(field.schema.__mapper__.c.uuid==column),
            foreign_keys=[column],
            enable_typechecks=False,
            lazy=True)
            }

class ListProperty(object):
    """A list property.

    Model the schema.List
    """

    def __call__(self, field, column, metadata):
        relation_table = metadata.tables['relation']
        soup_table = metadata.tables['soup']
        
        return {
            field.__name__: orm.relation(
                bootstrap.Relation,
                #secondary=relation_table,
                primaryjoin=soup_table.c.uuid==relation_table.c.left,
                #secondaryjoin=relation_table.c.target==soup_table.c.uuid,
                #foreign_keys=[relation_table.c.source],
                collection_class=RelationList,
                enable_typechecks=False)
            }
                    
class DictProperty(object):
    """A dict property.

    In SQLAlchemy, we need to model the following two defintion types:

       schema.Dict(
           value_type=schema.Object(
                schema=ISomeInterface)
           )

       schema.Dict(
           value_type=schema.Set(
                value_schema.Object(
                     schema=ISomeInterface)
                )
           )

    Reference:

    http://blog.discorporate.us/2008/02/sqlalchemy-partitioned-collections-1
    http://www.sqlalchemy.org/docs/04/mappers.html#advdatamapping_relation_collections
    
    """
    
    def __call__(self, field, column, metadata):
        #
        #
        # TODO: Return column definition

        pass
    
fieldmap = {
    schema.ASCII: StringTranslator(), 
    schema.ASCIILine: StringTranslator(),
    schema.Bool: FieldTranslator(rdb.BOOLEAN),
    schema.Bytes: FieldTranslator(rdb.BLOB),
    schema.BytesLine: FieldTranslator(rdb.BLOB),
    schema.Choice: StringTranslator(),
    schema.Date: FieldTranslator(rdb.DATE),
    schema.Dict: (ObjectTranslator(), DictProperty()),
    schema.DottedName: StringTranslator(),
    schema.Float: FieldTranslator(rdb.Float), 
    schema.Id: StringTranslator(),
    schema.Int: FieldTranslator(rdb.Integer),
    schema.List: (None, ListProperty()),
    schema.Object: (ObjectTranslator(), ObjectProperty()),
    schema.Password: StringTranslator(),
    schema.SourceText: StringTranslator(),
    schema.Text: StringTranslator(),
    schema.TextLine: StringTranslator(),
    schema.URI: StringTranslator(),
    interface.interface.Method: None,
}

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

    engine = component.getUtility(IDatabaseEngine)
    metadata = engine.metadata

    ignore = ('__name__',)

    # expand specification
    if interface.interfaces.IInterface.providedBy(spec):
        ifaces = set([spec.get(name).interface for name in schema.getFields(spec)])
        kls = object
    else:
        implemented = interface.implementedBy(spec)
        fields = chain(*[schema.getFields(iface) for iface in implemented])
        ifaces = set([implemented.get(name).interface for name in fields])
        kls = spec

    # create joined table
    soup_table = table = metadata.tables['soup']
    properties = {}
    
    for (t, p) in (getTable(iface, metadata, ignore) for iface in ifaces):
        table = rdb.join(table, t, onclause=(t.c.id==soup_table.c.id))
        properties.update(p)

    class Mapper(kls):
        interface.implements(IMapped, *ifaces)

        __spec__ = '%s.%s' % (spec.__module__, spec.__name__)

    # if the specification is an interface class, try to look up a
    # security checker and define it on the mapper
    if interface.interfaces.IInterface.providedBy(spec):
        checker = component.queryAdapter(spec, IChecker)
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

    exclude = ()
    
    if not interface.interfaces.IInterface.providedBy(spec):
        for name, value in spec.__dict__.items():
            if isinstance(value, property):
                exclude += (name,)

    orm.mapper(Mapper, table, properties=properties, exclude_properties=exclude)

    spec.__mapper__ = Mapper
    interface.alsoProvides(spec, IMapped)

    return Mapper

def removeMapper(spec):
    del spec.mapper
    interface.noLongerProvides(spec, IMapped)
        
def getTable(iface, metadata, ignore=()):
    columns = []
    properties = {}
    
    for field in map(lambda key: iface[key], iface.names()):
        property_factory = None

        # ignores
        if field.__name__ in ignore:
            continue
        
        try:
            column_factory, property_factory = fieldmap[type(field)]
        except TypeError:
            column_factory = fieldmap[type(field)]
        except KeyError:
            # raise NotImplementedError("Field type unsupported (%s)." % field)
            continue

        if column_factory is not None:
            column = column_factory(field, metadata)
            columns.append(column)
        else:
            column = None
            
        if property_factory is not None:
            props = property_factory(field, column, metadata)
            properties.update(props)
        
    kw = dict(useexisting=True)

    table = rdb.Table(
        encode(iface),
        metadata,
        rdb.Column('id', rdb.Integer, rdb.ForeignKey("soup.id"), primary_key=True),
        *columns,
        **kw)

    metadata.create_all(checkfirst=True)
    
    return table, properties
