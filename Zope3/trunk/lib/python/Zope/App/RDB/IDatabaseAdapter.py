from Interface import Interface

class IDatabaseAdapter(Interface):
    """ interface for persistent object that returns
    volatile IConnections. """

    def __call__():
        """return an Iconnection object"""

