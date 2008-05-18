from zope import component

import z3c.dobbin.bootstrap
import sqlalchemy as rdb

from sqlalchemy import orm

from ore.alchemist import Session
from ore.alchemist.interfaces import IDatabaseEngine

metadata = rdb.MetaData()

def setUp(test):
    test._engine = rdb.create_engine('sqlite:///:memory:')
    
    # register database engine
    component.provideUtility(test._engine, IDatabaseEngine)

    # bootstrap database engine
    z3c.dobbin.bootstrap.bootstrapDatabaseEngine(None)

def tearDown(test):
    del test._engine
    del metadata._bind
