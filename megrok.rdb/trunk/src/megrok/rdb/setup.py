from zope import component
from zope.event import notify

from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import instrument_declarative

from z3c.saconfig.interfaces import IEngineFactory
from megrok.rdb.interfaces import DatabaseSetupEvent

def setupDatabase(metadata):
    """Set up of ORM for engine in current site.

    This will:

    * reflect any reflected tables that need to be reflected from the database
      into classes.

    * create any tables in the database that haven't been yet reflected.    
    """
    reflectTables(metadata)
    createTables(metadata)
    notify(DatabaseSetupEvent(metadata))
    
def reflectTables(metadata):
    """Reflect tables into ORM.
    """
    if getattr(metadata, '_reflected_completed', False):
        # XXX thread safety?
        return
    if not getattr(metadata, '_reflected_registry', {}):
        # nothing to reflect
        return
    # first reflect database-defined schemas into metadata
    engine = Engine()
    metadata.reflect(bind=engine)
    if not hasattr(metadata, '_decl_registry'):
        metadata._decl_registry = {}
    # now declaratively set up any reflected classes
    for class_ in metadata._reflected_registry.keys():
        instrument_declarative(class_, metadata._decl_registry, metadata)
    # XXX thread safety?
    metadata._reflected_completed = True

def createTables(metadata):
    """Create class-specified tables.
    """
    engine = Engine()
    metadata.create_all(engine)

def Engine():
    """Get the engine in the current session.
    """
    engine_factory = component.getUtility(IEngineFactory)
    return engine_factory()
