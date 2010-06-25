from zope.interface import Interface


class IVersionSupport(Interface):

    def getVersionableData():
        """ Return versionable data """

    def restoreFromVersion(version_data):
        """ Restore object based on 'version_data' """


class IVersionStorage(Interface):

    def store(id, version_data):
        """ Store 'version_data' for a given 'id'.
            Returns revision number.
        """

    def retrieve(id, revision):
        """ Return 'version_data' for a given 'id' and 'revision' """

    def list_versions(id):
        """ Return all versions stored for a particular
            content piece by its 'id'.
        """
