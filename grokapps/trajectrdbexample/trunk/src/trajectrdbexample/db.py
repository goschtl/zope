"""
This module sets up the database, tables and models using SQLAlchemy
and z3c.saconfig.
"""

# we don't need to depend on Grok, just on grokcore.component
import grokcore.component as grok

from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy import MetaData

from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineCreatedEvent

# we set up the engine factory and the session
# we set them up as global utilities here. It is also possible to
# use a local engine factory and a special locally scoped session
# XXX for some reason it fails to work properly with a :memory: database
TEST_DSN = 'sqlite:///test.db'

engine_factory = EngineFactory(TEST_DSN)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)

metadata = MetaData()

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    # automatically create all tables if necessary as soon
    # as we first try to contact the database
    metadata.create_all(bind=event.engine)

# we sketch out a fully explicit SQLAlchemy ORM mapping
# the idea is to show that we can expose objects that are defined
# without knowledge of how they will appear on the web, using megrok.traject

faculty = Table(
    'faculty', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(50)))

department = Table(
    'department', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(50), unique=True),
    Column('faculty_id', Integer, ForeignKey('faculty.id')))
    
# it is possible to make this work without depending on
# grokcore.component (or Grok) at all. In this case, in a Grok application be
# aware that the browser default view for non-Grok objects is
# index.html, *not* index. You can turn your own objects into
# using 'index' by the following ZCML:
#
# <browser:defaultView for="my.Model" name="index" />
#
# In addition, Grok won't auto-associate views with your model
# and you have to use an explicit grok.context()

class Faculty(grok.Context):
    def __init__(self, title):
        self.title = title

class Department(grok.Context):
    def __init__(self, title):
        self.title = title
    
mapper(Faculty, faculty, properties={
        'departments': relation(
            Department, backref=backref('faculty')),
        })

mapper(Department, department)
