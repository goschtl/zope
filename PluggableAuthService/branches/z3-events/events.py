from zope.component import adapter
from zope.component import subscribers
from zope.interface import implements
from Products.PluggableAuthService.interfaces.events import *

class PASEvent(object):
    implements(IPASEvent)

    def __init__(self, acl_users, principal):
        self.acl_users=acl_users
        self.principal=principal
        self.object=principal


class PrincipalCreated(PASEvent):
    implements(IPrincipalCreatedEvent)


class PrincipalDeleted(PASEvent):
    implements(IPrincipalDeletedEvent)


class CredentialsUpdated(PASEvent):
    implements(ICredentialsUpdatedEvent)

    def __init__(self, acl_users, principal, password):
        super(CredentialsUpdated, self).__init__(acl_users, principal)
        self.password=password


class PropertiesUpdated(PASEvent):
    implements(IPropertiesUpdatedEvent)

    def __init__(self, acl_users, principal, properties):
        super(CredentialsUpdated, self).__init__(acl_users, principal)
        self.properties=properties


def userCredentialsUpdatedHandler(principal, event):
    event.acl_users.updateCredentials(
            event.acl_users,
            event.acl_users.REQUEST,
            event.acl_users.REQUEST.RESPONSE,
            principal.getId(),
            event.password)


@adapter(IPASEvent)
def PASEventNotify(event):
    """Event subscriber to dispatch PASEvent to interested adapters."""
    adapters = subscribers((event.principal, event), None)
    for adapter in adapters:
        pass # getting them does the work

