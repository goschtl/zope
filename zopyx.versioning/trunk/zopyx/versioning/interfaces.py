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


class IVersionStorage(Interface):

    def store(id, version_data, creator_id, comment):
        """ Store 'version_data' for a given 'id'.
            Returns revision number.
        """

    def retrieve(id, revision):
        """ Return 'version_data' for a given 'id' and 'revision' """

    def has_revision(id, revision):
        """ Check if there is a revison 'revision' for a given object 'id' """

    def remove_revision(id, revision):
        """ Remove a particular 'revision' for a given object 'id' """

    def remove_all(id):
        """ Remove all revisions for a given object 'id' """

    def list_revisions(id):
        """ Return all revisions stored for a particular
            content piece by its 'id'.
        """
