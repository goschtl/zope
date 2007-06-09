from zope.interface import implements
from Products.PluggableAuthService.interfaces.events import *

class PASEvent(object):
    implements(IPASEvent)

    def __init__(self, acl_users, userid):
        self.acl_users=acl_users
        self.userid=userid


class UserCreated(PASEvent):
    implements(IUserCreatedEvent)

    def __init__(self, acl_users, userid, login):
        self.acl_users=acl_users
        self.userid=userid
        self.login=login


class UserDeleted(PASEvent):
    implements(IUserDeletedEvent)


class UserCredentialsUpdated(PASEvent):
    implements(IUserCredentialsUpdatedEvent)

    def __init__(self, acl_users, userid, password):
        self.acl_users=acl_users
        self.userid=userid
        self.password=password


class UserPropertiesUpdated(PASEvent):
    implements(IUserPropertiesUpdatedEvent)

    def __init__(self, acl_users, userid, properties):
        self.acl_users=acl_users
        self.userid=userid
        self.properties=properties

def userCredentialsUpdatedHandler(event):
    event.acl_users.updateCredentials(
            event.acl_users,
            event.acl_users.REQUEST,
            event.acl_users.REQUEST.RESPONSE,
            event.userid,
            event.password)

