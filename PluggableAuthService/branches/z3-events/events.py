from interfaces.events import *

class PASEvent(object):
    implements(IPASEvent)

    def __init__(self, id):
        self.id=id


class UserCreated(PASEvent):
    implements(IUserCreated)

    def __init__(self, id, login):
        self.id=id
        self.login=login


class UserDeleted(PASEvent):
    implements(IUserDeleted)


class UserCredentialsUpdated(PASEvent):
    implements(IUserCredentialsUpdated)

    def __init__(self, id, password):
        self.id=id
        self.password=password


class UserPropertiesUpdated(PASEvent):
    implements(IUserPropertiesUpdated)

    def __init__(self, id, properties):
        self.id=id
        self.properties=properties
