from zope import component

import sqlalchemy as rdb
from sqlalchemy import orm
        
from ore.alchemist.interfaces import IDatabaseEngine

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

def soup(metadata):
    table = rdb.Table(
        'soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', rdb.String(length=32), unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        )

    orm.mapper(Soup, table)

def catalog(metadata):
    return rdb.Table(
        'catalog',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', rdb.String(length=32), rdb.ForeignKey("soup.uuid"), index=True),
        rdb.Column('right', rdb.String(length=32), rdb.ForeignKey("soup.uuid")),
        rdb.Column('name', rdb.String))

def relation(metadata):
    table = rdb.Table(
        'relation',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', rdb.String(length=32), rdb.ForeignKey("soup.uuid"), index=True),
        rdb.Column('right', rdb.String(length=32), rdb.ForeignKey("soup.uuid")),
        rdb.Column('order', rdb.Integer, nullable=False))
    
    orm.mapper(relations.Relation, table)

class Soup(object):
    pass
