from zope import interface
from zope import schema

class IUserCreated(interface.Interface):
    """A new user has been registered.
    """
    userid = schema.IASCIILine(
            title=u'User id',
            required=True)
    login = schema.IASCIILine(
            title=u'Login name',
            required=True)


class IUserDeleted(interface.Interface):
    """A user has been removed.
    """
    userid = schema.IASCIILine(
            title=u'User id',
            required=True)


class IUserCredentialsUpdated(interface.Interface):
    """A user has changed her password.
    """
    userid = schema.IASCIILine(
            title=u'User id',
            required=True)
    password = schema.IPassword(
            title=u'The new password',
            required=True)


class IUserPropertiesUpdated(interface.Interface):
    """A users properties have been updated.
    """
    userid = schema.IASCIILine(
            title=u'User id',
            required=True)
    properties = schema.IList(
            title=u'Modified properties',
            required=False)


