from zope import component

import sqlalchemy as rdb
from sqlalchemy import orm
        
from ore.alchemist.interfaces import IDatabaseEngine
from ore.alchemist import Session

from interfaces import IMapped

import relations

def bootstrapDatabaseEngine(event):
    engine = component.getUtility(IDatabaseEngine)
    engine.metadata = metadata = rdb.MetaData(engine)
    setUp(metadata)
    
def setUp(metadata):
    soup(metadata)
    catalog(metadata)
    relation(metadata)
    metadata.create_all()

class Soup(object):
    pass

def soup(metadata):
    table = rdb.Table(
        'soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', rdb.String(length=32), unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        )

    orm.mapper(Soup, table)

    return table

def catalog(metadata):
    return rdb.Table(
        'catalog',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', rdb.String(length=32), rdb.ForeignKey("soup.uuid"), index=True),
        rdb.Column('right', rdb.String(length=32), rdb.ForeignKey("soup.uuid")),
        rdb.Column('name', rdb.String))

class Relation(object):
    def _get_source(self):
        return relations.lookup(self.left)

    def _set_source(self, item):
        self.left = item.uuid

    def _get_target(self):
        return relations.lookup(self.right)

    def _set_target(self, item):
        if not IMapped.providedBy(item):
            item = relations.persist(item)

        if item.id is None:
            session = Session()
            session.save(item)
                
        self.right = item.uuid

    source = property(_get_source, _set_source)
    target = property(_get_target, _set_target)
    
def relation(metadata):
    table = rdb.Table(
        'relation',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', rdb.String(length=32), rdb.ForeignKey("soup.uuid"), index=True),
        rdb.Column('right', rdb.String(length=32), rdb.ForeignKey("soup.uuid")),
        rdb.Column('order', rdb.Integer, nullable=False))
    
    orm.mapper(Relation, table)
    
    return table
