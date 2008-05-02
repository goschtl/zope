from zope.interface import Interface, Attribute

from zope.app.container.interfaces import IContainer as IContainerBase


class IContainer(IContainerBase):
    def set(value):
        """Add a new value to the container without having to specify the key.

        Lets the container figure out an appropriate key.


        Defined by SQLAlchemy dictionary-based collections.
        """

    def remove(value):
        """Remove a value from the container, by value.

        
        Defined by SQLAlchemy dictionary-based collections.
        """

class IDatabase(Interface):
    # you have to implement this attribute to set up the connection URL
    url = Attribute(u"The connection URL of the database.")

    def setup(metadata):
        """Extra setup the database if required.

        Implement this method if you want to do extra setup for the database.
        
        The declarative base classes Model and Container already get set
        up automatically, but you may want to add extra tables and ORM mappers
        in this method.
        """
