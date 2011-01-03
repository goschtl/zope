import os
from zope.configuration import xmlconfig, config
from zope.component.hooks import setHooks
from zope.testing.cleanup import cleanUp
from zope import component
from zope.event import notify
from zope.app.publication.zopepublication import ZopePublication
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory

import zope.processlifetime

from zope.app import wsgi

from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage
import ZODB.interfaces

import transaction
import sys

def argument(func):
    def function(*args, **kwargs):
        return func(*args, **kwargs)

    name = 'pytest_funcarg__' + func.func_name
    function.func_name = name

    if func.__module__ is None:
        __builtins__[name] = function
        return function
    else:
        __import__(func.__module__)
        mod = sys.modules[func.__module__]
        setattr(mod, name, function)
        return getattr(mod, name)


def create_app(request, site_root):
    db = setup_db()
    connection = setup_connection(db)
    root = setup_root(connection)
    root['test'] = site_root

    wsgi_app = wsgi.WSGIPublisherApplication(
        db,
        HTTPPublicationRequestFactory,
        True)

    transaction.commit()

    def finalize():
        teardown_root(root)
        teardown_connection(connection)
        teardown_db(db)

    request.addfinalizer(finalize)

    # turn this off to let the errors be handled by the server
    # this is useful for testing the server's error handling
    wsgi_app.handleErrors = False

    return wsgi_app

def configure(request, module, zcml):
    def setup_function():
        return setup_config(module, zcml)

    return request.cached_setup(setup=setup_function,
                                teardown=teardown_config,
                                scope='session')

def setup_config(package, zcml_file):
    zcml_file = os.path.join(os.path.dirname(package.__file__),
                             zcml_file)

    setHooks()
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)

    return xmlconfig.file(zcml_file,
                          package=package,
                          context=context, execute=True)

def teardown_config(config):
    cleanUp()

def setup_db():
    name = 'main'
    storage = DemoStorage(name)
    db = DB(storage, database_name=name)
    db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

    # DB are registered as utilities
    component.provideUtility(db, ZODB.interfaces.IDatabase, name)

    # And we send a event that our DB is available
    notify(zope.processlifetime.DatabaseOpened(db))

    return db

def teardown_db(db):
    # Need to unregister DB
    base = component.getGlobalSiteManager()
    base.unregisterUtility(
        db, ZODB.interfaces.IDatabase, 'main')
    db.close()

def setup_connection(db):
    return db.open()

def teardown_connection(connection):
    transaction.abort()
    connection.close()

def setup_root(connection):
    return connection.root()[ZopePublication.root_name]

def teardown_root(root):
    pass

