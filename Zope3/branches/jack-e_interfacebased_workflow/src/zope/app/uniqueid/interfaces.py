"""
Interfaces for the unique id utility.

$Id$
"""
from zope.interface import Interface, Attribute, implements


class IReference(Interface):
    """A reference to an object (similar to a weak reference).

    The references are compared by their hashes.
    """

    def __call__():
        """Get the object this reference is linking to."""

    def __hash__():
        """Get a unique identifier of the referenced object."""


class IUniqueIdUtilityQuery(Interface):

    def getObject(uid):
        """Return an object by its unique id"""

    def getId(ob):
        """Get a unique id of an object.
        """

    def queryObject(uid, default=None):
        """Return an object by its unique id

        Return the default if the uid isn't registered
        """

    def queryId(ob, default=None):
        """Get a unique id of an object.

        Return the default if the object isn't registered
        """

class IUniqueIdUtilitySet(Interface):

    def register(ob):
        """Register an object and returns a unique id generated for it.

        If the object is already registered, its id is returned anyway.
        """

    def unregister(ob):
        """Remove the object from the indexes.

        ValueError is raised if ob is not registered previously.
        """

class IUniqueIdUtilityManage(Interface):
    """Some methods used by the view."""

    def __len__():
        """Return the number of objects indexed."""

    def items():
        """Return a list of (id, object) pairs."""


class IUniqueIdUtility(IUniqueIdUtilitySet, IUniqueIdUtilityQuery,
                       IUniqueIdUtilityManage):
    """A utility that assigns unique ids to objects.

    Allows to query object by id and id by object.
    """


class IUniqueIdRemovedEvent(Interface):
    """The event which is published before the unique id is removed
    from the utility so that the catalogs can unindex the object.
    """

    original_event = Attribute(
        """The IObjectRemoveEvent related to this event""")


class UniqueIdRemovedEvent(object):
    """The event which is published before the unique id is removed
    from the utility so that the catalogs can unindex the object.
    """

    implements(IUniqueIdRemovedEvent)

    def __init__(self, event):
        self.original_event = event


class IUniqueIdAddedEvent(Interface):
    """The event which gets sent when an object is registered in a
    unique id utility.
    """
    original_event = Attribute("The ObjectAddedEvent related to this event")


class UniqueIdAddedEvent:
    """The event which gets sent when an object is registered in a
    unique id utility.
    """
    implements(IUniqueIdAddedEvent)
    def __init__(self, event):
        self.original_event = event
