from zope import interface
from zope import component

import sqlalchemy as rdb
from sqlalchemy import orm

from z3c.saconfig import Session

import soup
import utility
import relations
import interfaces
import cPickle

class UUID(rdb.types.TypeEngine):
    def get_col_spec(self):
        return "UUID"

def get_soup_table():
    return Soup._sa_class_manager.mapper.local_table

def initialize(event=None):
    """Database initialization.

    This method sets up the tables that are necessary for the
    operation of the persistence and relational framework.
    """

    session = Session()
    engine = session.bind
    engine.metadata = metadata = rdb.MetaData(engine)
    
    soup = rdb.Table(
        'dobbin:soup',
        metadata,
        rdb.Column('id', rdb.Integer, primary_key=True, autoincrement=True),
        rdb.Column('uuid', UUID, unique=True, index=True),
        rdb.Column('spec', rdb.String, index=True),
        rdb.Column('dict', rdb.PickleType, default={}, index=False),
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
    interface.implements(interfaces.IMapped)
    
    """Soup class.

    This is the base object of all mappers.
    """

    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls, *args, **kwargs)
        inst.__dict__ = utility.dictproxy(inst)
        return inst
    
    def __cmp__(self, other):
        if interfaces.IMapped.providedBy(other):
            return cmp(self.id, other.id)

        return -1

    def __reduce__(self):
        return (soup.build, (self.__spec__, self.uuid,))
