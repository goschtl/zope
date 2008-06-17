"""An experiment in integration with SQLAlchemy.

The main goal of this experiment is to allow the user to instantiate a
Session object in the normal SQLAlchemy way. This session object is
however also fully aware of Zope transactions (thanks to
zope.sqlalchemy), and moreover, is managed automatically by SQLAlchemy
per-thread and per-application, using SQLAlchemy's ScopedSession.

The applications to install expose 2 relevant URLs:

* index - edit the name of the engine this app uses. (engine1, engine2)

* db - do a simple db query

The application expects a database with a 'test' table, which has an
'id' primary key and a 'name' text column. These databases are
currently Postgresql databases, experiment and experiment2. For the
experiment, they should each have different information the test table
(name column).

You can create applications and set their engine using the index
view. You can then use 'db' to look at the query. The result should be
different if you set the engine differently. If you change the engine
while the application is running, it will have no effect as the same
session will still be reused (with the old engine bound to it). Instead
you can restart the application to see the effect.

This experiment will hopefully result in a new Zope 3 extension that
allows the use of this pattern of configuration.

Note that this experiment uses Grok, but the fundamental mechanics are
not related to Grok. The ORM mapping bits are also just to test whether
things work, not fundamental to the example.
"""

import grok
from zope import schema

from sqlalchemy.orm import scoped_session
from zope import component
from zope.interface import Interface
import thread
from sqlalchemy.orm import mapper
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import create_engine
import sqlalchemy as sa

class IDatabase(Interface):
    """A utility that specifies the database.
    """

    def session_factory():
        """Create the session.

        The session needs to be configured with the right engine and
        parameters.

        The session is only created one per thread/application combination.
        """

    def scopefunc():
        """Determine the scope of the session.
        
        This should at the very least be unique per thread.
        """

class Database(grok.LocalUtility):
    grok.implements(IDatabase)

    def session_factory(self):
        print "creating new session"
        return sa.orm.create_session(**self.configuration())

    def scopefunc(self):
        # we use the application name as the unique per application id.
        # Can we use something more clever and universally working?
        result = (thread.get_ident(), self.__parent__.__name__)
        print "scopefunc:", result
        return result
    
    def engine(self):
        # we look up the engine with the name defined in the application
        return component.getUtility(IEngine, self.__parent__.engine_name)
    
    def configuration(self):
        # we return the configuration parameters as for an
        # SQLAlchemy sessionmaker
        return dict(
            bind=self.engine(),
            autocommit=True,
            autoflush=True,
            extension=ZopeTransactionExtension())

def session_factory():
    """This is used by scoped session to create a new Session object.
    """
    utility = component.getUtility(IDatabase)
    return utility.session_factory()

def scopefunc():
    """This is used by scoped session to distinguish between sessions.
    """
    utility = component.getUtility(IDatabase)
    return utility.scopefunc()

# this is a frame-work central configuration, we only need to do this
# once in our integration framework, after which we can just import
# Session
Session = scoped_session(session_factory, scopefunc)

class IEngine(Interface):
    """The database engine.
    """
    
# we register the available engines as global utilities.
# we want to be able to configure the engines, preferably also through
# the UI. This might mean we need to register the engine as a local,
# non-persistent utility that is somehow recreated on each restart.
engine1 = create_engine('postgres:///experiment', convert_unicode=True)
grok.global_utility(engine1, provides=IEngine, direct=True, name='engine1')

engine2 = create_engine('postgres:///experiment2', convert_unicode=True)
grok.global_utility(engine2, provides=IEngine, direct=True, name='engine2')

# an application that allows the configuration of the engine name
class IForm(Interface):
    engine_name = schema.TextLine(title=u"Engine name")

class App(grok.Application, grok.Container):
    grok.local_utility(Database, provides=IDatabase, public=True,
                       name_in_container='database')

    grok.implements(IForm)
    
    engine_name = ''

class Index(grok.EditForm):
    grok.context(App)

    form_fields = grok.Fields(IForm)

    @grok.action("Submit")
    def submit(self, engine_name):
        self.context.engine_name = engine_name

# here we define the table information and inform the ORM of the mapping
# this is not part of the experiment, just so we can test things.
class Test(object):
    """An object that is mapped with the ORM"""
    pass

metadata = sa.MetaData()
test_table = sa.Table('test', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('name', sa.Text))
mapper(Test, test_table)

# the db view does a query in the Test table using the ORM. It uses
# an instance of Session to do so. This is to verify that our scoped session
# is working; it will automatically use a cached session.
class Db(grok.View):
    grok.context(App)

    def render(self):
        # this is the normal SQLAlchemy usage: just instantiate
        # Session. No special Zope-related lookup logic
        session = Session()
        result = session.query(Test).all()
        return repr([obj.name for obj in result])
