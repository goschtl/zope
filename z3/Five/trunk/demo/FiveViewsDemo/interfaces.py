from zope.interface import Interface

class ISimpleContent(Interface):
    def mymethod():
        """This is just a sample method.
        """

class IFolder(Interface):
    pass


class IReadSimpleFolderView(Interface):

    def eagle():
        """Just a sample method"""

class IWriteSimpleFolderView(Interface):

    def mydefault():
        """Just a sample method"""

class ISimpleFolderView(IReadSimpleFolderView, IWriteSimpleFolderView):
    """Interface for SimpleFolderView"""
