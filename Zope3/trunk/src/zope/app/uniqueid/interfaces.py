"""
Interfaces for the unique id utility.

$Id$
"""
from zope.interface import Interface


class IReference(Interface):
    """A reference to an object (like a weak ref)

    Have to be orderable.  The references are only equal if they
    reference the same object.
    """

    def __call__():
        """Get the object this reference is linking to"""


class IUniqueIdUtilityQuery(Interface):

    def getObject(uid):
        """Return an object by its unique id"""

    def getId(ob):
        """Get a unique id of an object.

        If the id for an object is unknown, ValueError is raised.
        """

class IUniqueIdUtilitySet(Interface):

    def register(ob):
        """Registers an object and returns a unique id generated for it.

        If the object is already registered, its id is returned anyway.
        """

    def unregister(ob):
        """Remove the object from the indexes.

        ValueError is raised if ob is not registered previously.
        """

class IUniqueIdUtilityManage(Interface):
    """Some methods used by the view"""

    def __len__():
        """Returns the number of objects indexed"""

    def items():
        """Returns a list of (id, object) pairs"""


class IUniqueIdUtility(IUniqueIdUtilitySet, IUniqueIdUtilityQuery,
                       IUniqueIdUtilityManage):
    """A utility that assigns unique ids to the objects

    Allows to query object by id and id by object.
    """
