from zope import component

import zope.configuration.xmlconfig

import z3c.dobbin.bootstrap
import sqlalchemy as rdb

from sqlalchemy import orm

from ore.alchemist import Session
from ore.alchemist.interfaces import IDatabaseEngine

import z3c.dobbin

metadata = rdb.MetaData()

def setUp(test):
    test._engine = rdb.create_engine('sqlite:///:memory:')
    
    # register database engine
    component.provideUtility(test._engine, IDatabaseEngine)

    # bootstrap database engine
    z3c.dobbin.bootstrap.bootstrapDatabaseEngine(None)

    # register components
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', component)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.dobbin)()

def tearDown(test):
    del test._engine
    del metadata._bind
