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

class FieldTranslator(object):
    """Translate a zope schema field to a SQLAlchemy column."""

    column_type = default = None

    def __init__(self, column_type=None, default=None):
        self.column_type = column_type or self.column_type
        self.default = default

    def extractInfo( self, field, info ):
        d = {}
        d['name'] = field.getName()
        if field.required:
            d['nullable'] = False

        if field.default is None:
            d['default'] = self.default
        else:
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

        if field.default is None and not d.get('default'):
            d['default'] = u""
        
        return d

class ObjectTranslator(object):
    def __call__(self, field, metadata):
        return rdb.Column(
            field.__name__+'_uuid', bootstrap.UUID, nullable=False)

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
            primaryjoin=bootstrap.Soup.uuid==column,
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
        return bootstrap.Soup.uuid==relations.OrderedRelation.left
    
class TupleProperty(ListProperty):
    collection_class = collections.Tuple
                    
class DictProperty(CollectionProperty):
    collection_class = collections.Dict
    relation_class = relations.KeyRelation

    def getPrimaryJoinCondition(self):
        return bootstrap.Soup.uuid==relations.KeyRelation.left
                        
fieldmap = {
    schema.ASCII: StringTranslator(), 
    schema.ASCIILine: StringTranslator(),
    schema.Bool: FieldTranslator(rdb.BOOLEAN, default=False),
    schema.Bytes: FieldTranslator(rdb.BLOB),
    schema.BytesLine: FieldTranslator(rdb.CLOB),
    schema.Choice: StringTranslator(rdb.Unicode),
    schema.Date: FieldTranslator(rdb.DATE),
    schema.Dict: (None, DictProperty()),
    schema.DottedName: StringTranslator(),
    schema.Float: FieldTranslator(rdb.Float, default=0), 
    schema.Id: StringTranslator(rdb.Unicode),
    schema.Int: FieldTranslator(rdb.Integer, default=0),
    schema.List: (None, ListProperty()),
    schema.Tuple: (None, TupleProperty()),
    schema.Object: (ObjectTranslator(), ObjectProperty()),
    schema.Password: StringTranslator(rdb.Unicode),
    schema.SourceText: StringTranslator(rdb.UnicodeText),
    schema.Text: StringTranslator(rdb.UnicodeText),
    schema.TextLine: StringTranslator(rdb.Unicode),
    schema.URI: StringTranslator(rdb.Unicode),
    interface.Attribute: None,
    interface.interface.Method: None,
}
