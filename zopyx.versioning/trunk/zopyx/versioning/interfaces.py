################################################################
# zopyx.versioning
# (C) 2010, ZOPYX Ltd, D-72070 Tuebingen
# Published under the Zope Public License 2.1
################################################################


""" 
Interfaces related to the versioning API
"""

from zope.interface import Interface

class IVersionSupport(Interface):
    """ API for retrieving data to be versioned from an object
        and restoring a previous state of an object.
        The data format is JSON.

        Objects must provide their unique ID through the 'id' field.

        This API applies to single objects only 
        (no support for object collections).
    """

    def getVersionableData():
        """ Return versionable data (in JSON format) """

    def restoreFromVersion(version_data):
        """ Restore object based on 'version_data' (JSON format) """

class ICollectionVersionSupport(Interface):
    """ API for retrieving the objects of a collection
        (a folder, a site, ...) to be versioned.
    """

    def getVersionableItems():
        """ Returns a sequence of objects IDs to be versioned """

    # XXX - no need for a getRestorableItems() method since the information
    # about items to be restored are part of the information stored in the
    # storage backend.

class IVersionID(Interface):
    
    def getID():
        """ Return a unique and stable ID for the object to be versioned """

class IVersionStorage(Interface):

    # methods used for IVersionSupport
    def store(id, version_data, revision_metadata):
        """ Store 'version_data' for a given 'id'.  'version_data' holds the
            data to be versioned (JSON format).  'revision_metadata' holds
            application-specific metadata for the particular version (e.g. 
            revision date, creator uid, "revision is a major/minor 
            revision) (JSON format).

            Returns revision number.
        """

    def retrieve(id, revision):
        """ Return 'version_data' for a given 'id' and 'revision' """

    def remove(id):
        """ Remove all revisions for a given object 'id' """

    def has_revision(id, revision):
        """ Check if there is a revison 'revision' for a given object 'id' """

    def remove_revision(id, revision):
        """ Remove a particular 'revision' for a given object 'id' """

    def remove(id):
        """ Remove all revisions for a given object 'id' """

    def list_revisions(id):
        """ Return all revisions (and their stored revison_metadata) stored for
            a particular content piece by its 'id'.
        """

    # methods used for ICollectionVersionSupport
    # XXX to be written#


class IVersioning(Interface):

    def getStorage(dsn):
        """ Provide access to a version storage based on a DSN """


class ILookup(Interface):

    def getObjectById(id):
        """ Retrieve an object by its ids from a collection or 
            "site" (whatever that means).
        """
