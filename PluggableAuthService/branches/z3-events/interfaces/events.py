from zope.interface import Attribute, Interface

class IPASEvent(Interface):
    """An event related to a PAS principal.
    """

    id = Attribute('Principal id')


class IPASUserEvent(IPASEvent):
    """An event related to a PAS user.
    """


class IPASGroupEvent(IPASEvent):
    """An event related to a PAS group.
    """


class IUserCreated(IPASUserEvent):
    """A new user has been registered.
    """
    login = Attribute('Login name')


class IUserDeleted(IPASUserEvent):
    """A user has been removed.
    """


class IUserCredentialsUpdated(IPASUserEvent):
    """A user has changed her password.
    """
    password = Attribute('The new password')


class IUserPropertiesUpdated(IPASUserEvent):
    """A users properties have been updated.
    """
    properties = Attribute('List of modified properties')


