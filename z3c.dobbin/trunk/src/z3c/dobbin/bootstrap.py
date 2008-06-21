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
    uuid = rdb.String(length=32)
    fk = rdb.ForeignKey("soup.uuid")
    
    soup = rdb.Table(
        'soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', uuid, unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        )

    relation = rdb.Table(
        'relation',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', uuid, fk, index=True),
        rdb.Column('right', uuid, fk),
        rdb.Column('order', rdb.Integer, nullable=False))

    catalog = rdb.Table(
        'catalog',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', uuid, fk, index=True),
        rdb.Column('right', uuid, fk),
        rdb.Column('name', rdb.String))
    
    orm.mapper(relations.Relation, relation)
    orm.mapper(Soup, soup)
    
    metadata.create_all()

class Soup(object):
    pass
