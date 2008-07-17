##############################################################################
#
# Parts of this module is copyright (c) 2008 Kapil Thangavelu
# <kapil.foss@gmail.com>. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope import interface
from zope import schema

import sqlalchemy as rdb
from sqlalchemy import orm
from z3c.saconfig import Session

import session as tx
import bootstrap
import relations
import collections

import cPickle as Pickle

class FieldTranslator( object ):
    """ Translate a zope schema field to an sa  column
    """

    def __init__(self, column_type):
        self.column_type = column_type

    def extractInfo( self, field, info ):
        d = {}
        d['name'] = field.getName()
        if field.required:
            d['nullable'] = False
        d['default'] = field.default
        d['type'] = self.column_type        
        return d
    
    def __call__(self, field, annotation):
        d = self.extractInfo( field, annotation )
        name, type = d['name'], d['type']
        del d['name']
        del d['type']
        return rdb.Column( name, type, **d)

class StringTranslator(FieldTranslator):
    
    column_type = rdb.Text

    def __init__(self, column_type=None):
        self.column_type = column_type or self.column_type
        
    def extractInfo( self, field, info ):
        d = super( StringTranslator, self ).extractInfo( field, info )
        if schema.interfaces.IMinMaxLen.providedBy( field ):
            d['type'].length = field.max_length
        return d

class ObjectTranslator(object):
    def __call__(self, field, metadata):
        return rdb.Column(
            field.__name__+'_uuid', bootstrap.UUID, nullable=False)

class PickleTranslator(object):
    def __call__(self, field, metadata):
        return rdb.Column(
            field.__name__+'_pickle', rdb.BLOB, nullable=True)

class PickleProperty(property):
    def __init__(self, name):
        self.name = name
        self.cache = '_v_cached_'+name
        property.__init__(self, self._get, self._set)
        
    def _get(self, obj, type=None):
        session = Session()
        name = self.name
        cache = self.cache
        
        token = tx.COPY_VALUE_TO_INSTANCE(obj.uuid, name)

        # check pending objects
        try:
            return session._d_pending[token]
        except (AttributeError, KeyError):
            pass

        # check object cache
        value = getattr(obj, cache, None)
        if value is not None:
            return value

        # load pickle
        pickle = getattr(obj, name)
        value = pickle and Pickle.loads(pickle)

        # update cache
        if value is not None:
            setattr(obj, cache, value)
        
        return value

    def _set(self, obj, value):
        name = self.name
        token = tx.COPY_VALUE_TO_INSTANCE(obj.uuid, name)
        
        def copy_value_to_instance():
            value = Session()._d_pending[token]
            pickle = Pickle.dumps(value)
            setattr(obj, name, pickle)

        # add transaction hook
        tx.addBeforeCommitHook(
            token, value, copy_value_to_instance)

        # update cache
        if value is not None:
            setattr(obj, self.cache, value)

class PicklePropertyFactory(object):
    def __call__(self, field, column, metadata):
        return {field.__name__: PickleProperty(column.name)}
    
class ObjectProperty(object):
    """Object property.

    We're not checking type here, because we'll only be creating
    relations to items that are joined with the soup.
    """

    def __call__(self, field, column, metadata):
        relation = relations.RelationProperty(field)

        return {
            field.__name__: relation,
            relation.name: orm.relation(
            bootstrap.Soup,
            primaryjoin=bootstrap.Soup.c.uuid==column,
            foreign_keys=[column],
            enable_typechecks=False,
            lazy=True)
            }

class CollectionProperty(object):
    """A collection property."""

    collection_class = None
    relation_class = None
    
    def __call__(self, field, column, metadata):
        return {
            field.__name__: orm.relation(
                self.relation_class,
                primaryjoin=self.getPrimaryJoinCondition(),
                collection_class=self.collection_class,
                enable_typechecks=False)
            }

    def getPrimaryJoinCondition(self):
        return NotImplementedError("Must be implemented by subclass.")
    
class ListProperty(CollectionProperty):
    collection_class = collections.OrderedList
    relation_class = relations.OrderedRelation

    def getPrimaryJoinCondition(self):
        return bootstrap.Soup.c.uuid==relations.OrderedRelation.c.left
    
class TupleProperty(ListProperty):
    collection_class = collections.Tuple
                    
class DictProperty(CollectionProperty):
    collection_class = collections.Dict
    relation_class = relations.KeyRelation

    def getPrimaryJoinCondition(self):
        return bootstrap.Soup.c.uuid==relations.KeyRelation.c.left
                        
fieldmap = {
    schema.ASCII: StringTranslator(), 
    schema.ASCIILine: StringTranslator(),
    schema.Bool: FieldTranslator(rdb.BOOLEAN),
    schema.Bytes: FieldTranslator(rdb.BLOB),
    schema.BytesLine: FieldTranslator(rdb.CLOB),
    schema.Choice: StringTranslator(rdb.Unicode),
    schema.Date: FieldTranslator(rdb.DATE),
    schema.Dict: (None, DictProperty()),
    schema.DottedName: StringTranslator(),
    schema.Float: FieldTranslator(rdb.Float), 
    schema.Id: StringTranslator(rdb.Unicode),
    schema.Int: FieldTranslator(rdb.Integer),
    schema.List: (None, ListProperty()),
    schema.Tuple: (None, TupleProperty()),
    schema.Object: (ObjectTranslator(), ObjectProperty()),
    schema.Password: StringTranslator(rdb.Unicode),
    schema.SourceText: StringTranslator(rdb.UnicodeText),
    schema.Text: StringTranslator(rdb.UnicodeText),
    schema.TextLine: StringTranslator(rdb.Unicode),
    schema.URI: StringTranslator(rdb.Unicode),
    interface.Attribute: (PickleTranslator(), PicklePropertyFactory()),
    interface.interface.Method: None,
}
