from Interface import Interface

class IZopeDatabaseAdapter(Interface):
    """ interface for persistent object that returns
    volatile IConnections.

    This object is internal to the connection service."""

    def __call__():
        """return an IZopeConnection object"""

