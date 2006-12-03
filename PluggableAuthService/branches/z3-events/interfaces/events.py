from zope.interface import Attribute, Interface

class IUserCreated(Interface):
    """A new user has been registered.
    """
    userid = Attribute('User id')
    login = Attribute('Login name')


class IUserDeleted(interface.Interface):
    """A user has been removed.
    """
    userid = Attribute('User id')


class IUserCredentialsUpdated(interface.Interface):
    """A user has changed her password.
    """
    userid = Attribute('User id')
    password = Attribute('The new password')


class IUserPropertiesUpdated(interface.Interface):
    """A users properties have been updated.
    """
    userid = Attribute('User id')
    properties = Attribute('List of modified properties')


