from interfaces.events import *

class PASEvent(object):
    implements(IPASEvent)

    def __init__(self, acl_users, id):
        self.acl_users=acl_users
        self.id=id


class UserCreated(PASEvent):
    implements(IUserCreated)

    def __init__(self, acl_users, id, login):
        self.acl_users=acl_users
        self.id=id
        self.login=login


class UserDeleted(PASEvent):
    implements(IUserDeleted)


class UserCredentialsUpdated(PASEvent):
    implements(IUserCredentialsUpdated)

    def __init__(self, acl_users, id, password):
        self.acl_users=acl_users
        self.id=id
        self.password=password


class UserPropertiesUpdated(PASEvent):
    implements(IUserPropertiesUpdated)

    def __init__(self, acl_users, id, properties):
        self.acl_users=acl_users
        self.id=id
        self.properties=properties
