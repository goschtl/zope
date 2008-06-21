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
    soup_uuid = rdb.String(length=32)
    soup_fk = rdb.ForeignKey("dobbin:soup.uuid")
    
    soup = rdb.Table(
        'dobbin:soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', soup_uuid, unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        )

    int_relation = rdb.Table(
        'dobbin:relation:int',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', soup_uuid, soup_fk, index=True),
        rdb.Column('right', soup_uuid, soup_fk),
        rdb.Column('order', rdb.Integer, nullable=False))

    catalog = rdb.Table(
        'catalog',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', soup_uuid, soup_fk, index=True),
        rdb.Column('right', soup_uuid, soup_fk),
        rdb.Column('name', rdb.String))
    
    orm.mapper(relations.OrderedRelation, int_relation)
    orm.mapper(Soup, soup)
    
    metadata.create_all()

class Soup(object):
    pass
