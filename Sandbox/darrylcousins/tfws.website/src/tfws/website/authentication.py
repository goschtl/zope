import zope.interface
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.app.component import hooks
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from z3c.authentication.simple import member
from z3c.authentication.simple import group

import grok

from tfws.website import interfaces
from tfws.website import roles
from tfws.website import permissions

grok.define_permission(permissions.VIEW)
grok.define_permission(permissions.MANAGEUSERS)
grok.define_permission(permissions.MANAGESITE)
grok.define_permission(permissions.MANAGECONTENT)

def setup_site_auth(auth):    

    # setup credentials plugin
    cred = SessionCredentialsPlugin()
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(cred))
    auth[u'credentials'] = cred
    auth.credentialsPlugins += (u'credentials',)

    site = auth.__parent__.__parent__
    prm = IPrincipalRoleManager(site)

    # setup 'members' member container
    members = member.MemberContainer()
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(members))
    auth[u'members'] = members
    auth.authenticatorPlugins += (u'members',)

    # setup 'groups' group container
    groups = group.GroupContainer(u'groups.')
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(groups))
    auth[u'groups'] = groups
    auth.authenticatorPlugins += (u'groups',)

    # setup 'Members' group
    grp =  group.Group(u'Members', u'Members')
    groups.addGroup('Members', grp) 
    prm.assignRoleToPrincipal(roles.MEMBER, 'groups.Members')

    # setup 'Administrators' group
    grp =  group.Group(u'Administrators', u'Administrators')
    groups.addGroup('Administrators', grp) 
    prm.assignRoleToPrincipal(roles.ADMINISTRATOR, 'groups.Administrators')

def role_factory(*args):
    def factory():
        return LocalRole(*args)
    return factory

def folder_factory(folderfactory, *args):
    def factory():
        return folderfactory(*args)
    return factory

class WebSiteMember(member.Member):
    """An IMember for MemberContainer."""

    zope.interface.implements(interfaces.IWebSiteMember)

    firstName = FieldProperty(interfaces.IWebSiteMember['firstName'])
    lastName = FieldProperty(interfaces.IWebSiteMember['lastName'])
    email = FieldProperty(interfaces.IWebSiteMember['email'])

    def __init__(self, login, password, firstName, lastName, email):
        title = firstName +' '+ lastName
        super(WebSiteMember, self).__init__(login, password, title)
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.description = email

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.title)

