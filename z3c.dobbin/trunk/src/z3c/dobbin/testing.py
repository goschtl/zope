from zope import component

import zope.configuration.xmlconfig

import z3c.dobbin.bootstrap
import sqlalchemy as rdb

from sqlalchemy import orm

import z3c.dobbin

from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession

metadata = rdb.MetaData()

def setUp(test):
    # provide engine factory
    factory = EngineFactory('sqlite:///:memory:')
    component.provideUtility(factory)

    # setup scoped session
    utility = GloballyScopedSession()
    component.provideUtility(utility)
    
    # bootstrap database engine
    z3c.dobbin.bootstrap.initialize()

    # register components
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', component)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.dobbin)()

def tearDown(test):
    pass
