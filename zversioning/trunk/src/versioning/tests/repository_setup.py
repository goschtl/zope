"""Some setup stuff not being intresting for doc tests
"""

import persistent
import zope.interface
import zope.app.annotation.attribute
import zope.app.annotation.interfaces
import zope.app.traversing.interfaces
from zope.app.versioncontrol import interfaces

def buildDatabaseRoot():
    """Opens a connection to a test database and returns the root object
    """
    from zope.app.tests import ztapi
    ztapi.provideAdapter(zope.app.annotation.interfaces.IAttributeAnnotatable,
                         zope.app.annotation.interfaces.IAnnotations,
                         zope.app.annotation.attribute.AttributeAnnotations)
    
    # Now we need to create a database with an instance of our sample object 
    # to work with:
    
    from ZODB.tests import util
    db = util.DB()
    connection = db.open()
    return connection.root()

def buildOldStyleRepository():
    """Setup a zope.app.versioncontrol repository
    
    Placing an object under version control requires an instance of an
    `IVersionControl` object.  This package provides an implementation of 
    this interface on the `Repository` class (from
    `zope.app.versioncontrol.repository`).  Only the `IVersionControl` 
    instance is responsible for providing version control operations; 
    an instance should never be asked to perform operations directly.
    """
    import zope.app.versioncontrol.repository
    import zope.interface.verify
    
    repository = zope.app.versioncontrol.repository.Repository()
    assert zope.interface.verify.verifyObject(
               interfaces.IVersionControl,
               repository)

    # In order to actually use version control, there must be an
    # interaction.  This is needed to allow the framework to determine the
    # user making changes.  Let's set up an interaction now. First we need a
    # principal. For our purposes, a principal just needs to have an id:
    class FauxPrincipal:
       def __init__(self, id):
           self.id = id
    principal = FauxPrincipal('bob')

    # Then we need to define an participation for the principal in the
    # interaction:
    class FauxParticipation:
        interaction=None
        def __init__(self, principal):
            self.principal = principal
    participation = FauxParticipation(principal)

    # Finally, we can create the interaction:
    import zope.security.management
    zope.security.management.newInteraction(participation)

    return repository
