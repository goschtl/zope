from zope.interface import implements
from interfaces.events import *

class PASEvent(object):
    implements(IPASEvent)

    def __init__(self, acl_users, userid):
        self.acl_users=acl_users
        self.userid=userid


class UserCreated(PASEvent):
    implements(IUserCreated)

    def __init__(self, acl_users, userid, login):
        self.acl_users=acl_users
        self.userid=userid
        self.login=login


class UserDeleted(PASEvent):
    implements(IUserDeleted)


class UserCredentialsUpdated(PASEvent):
    implements(IUserCredentialsUpdated)

    def __init__(self, acl_users, userid, password):
        self.acl_users=acl_users
        self.userid=userid
        self.password=password


class UserPropertiesUpdated(PASEvent):
    implements(IUserPropertiesUpdated)

    def __init__(self, acl_users, userid, properties):
        self.acl_users=acl_users
        self.userid=userid
        self.properties=properties
