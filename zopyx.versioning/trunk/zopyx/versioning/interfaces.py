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

class IVersionableCollection(Interface):
    """ Marker interface for an object collection with
        versionable content.
    """

class IVersionableCollectionPolicy(Interface):
    """ Interface used for implementing arbitrary
        versioning policies for object collections.
        (implemented through an adapter implementing
        IVersionableCollectionPolicy and adapting to
        IVersionableCollection.
    """

    def getVersionableObjects(self):
        """ Returns a sequence (or a generator) of objects
            from the collection to be versioned .
        """

class IVersionID(Interface):

    def getID():
        """ Return a unique and stable ID for the object to be versioned """

class IVersionStorage(Interface):

    def store(id, version_data, revision_metadata, collection_content=[]):
        """ Store 'version_data' for a given 'id'.  'version_data' holds the
            data to be versioned (JSON format).  'revision_metadata' holds
            application-specific metadata for the particular version (e.g. 
            revision date, creator uid, "revision is a major/minor 
            revision) (JSON format).

            If 'collection_content' is used then we assume that we version
            a collection of objects where the versioned objects are given
            as a list of tuples (object_id, object_revision).

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

class IVersioning(Interface):

    def getStorage(dsn):
        """ Provide access to a version storage based on a DSN """

