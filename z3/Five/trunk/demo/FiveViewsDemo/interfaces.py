from zope.interface import Interface

class IPublicSimpleContent(Interface):

    def mymethod():
        """This is just a sample method.
        """
class IPrivateSimpleContent(Interface):

    def myprivatemethod():
        """This is just a sample method.
        """

class IProtectedSimpleContent(Interface):

    def myprotectedmethod():
        """This is just a sample method.
        """

class ISimpleContent(IPublicSimpleContent,
                     IPrivateSimpleContent,
                     IProtectedSimpleContent):
    """A Simple Content Interface"""

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
