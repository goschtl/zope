from zope import component

import sqlalchemy as rdb
from sqlalchemy import orm
        
import ore.alchemist.interfaces
import relations

class UUID(rdb.types.TypeEngine):
    def get_col_spec(self):
        return "UUID"

def bootstrapDatabaseEngine(event):
    engine = component.getUtility(ore.alchemist.interfaces.IDatabaseEngine)
    engine.metadata = metadata = rdb.MetaData(engine)
    setUp(metadata)
    
def setUp(metadata):
    """Table setup.

    This method sets up the tables that are necessary for the
    operation of the persistence and relational framework.
    """
    
    soup = rdb.Table(
        'dobbin:soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', UUID, unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        )

    soup_fk = rdb.ForeignKey(soup.c.uuid)

    int_relation = rdb.Table(
        'dobbin:relation:int',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', UUID, soup_fk, index=True),
        rdb.Column('right', UUID, soup_fk),
        rdb.Column('order', rdb.Integer, nullable=False))

    str_relation = rdb.Table(
        'dobbin:relation:str',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('left', UUID, soup_fk, index=True),
        rdb.Column('right', UUID, soup_fk),
        rdb.Column('key', rdb.Unicode, nullable=False))

    # set up mappers
    orm.mapper(Soup, soup)
    orm.mapper(relations.OrderedRelation, int_relation)
    orm.mapper(relations.KeyRelation, str_relation)

    # create all tables
    metadata.create_all()

class Soup(object):
    """Soup class.

    This stub is used as the mapper for the soup table.
    """
