##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app import folder
from zope.app.component import site
from zope.app.security.interfaces import IAuthentication
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from z3c.authentication.simple.authentication import SimpleAuthentication
from z3c.authentication.simple.group import Group
from z3c.authentication.simple.group import GroupContainer
from z3c.authentication.simple.member import Member
from z3c.authentication.simple.member import MemberContainer

from z3c.authentication.simple.interfaces import IAuthenticatedPrincipal
from z3c.authentication.simple.interfaces import IFoundPrincipal
from z3c.authentication.simple.principal import PrincipalBase
from z3c.authentication.simple import member
from z3c.configurator import configurator
from z3c.resource.interfaces import IResource

from z3c.website import interfaces
from z3c.website import page
from z3c.website import sample


class WebSite(folder.Folder):
    """Website."""

    zope.interface.implements(interfaces.IWebSite)

    title = FieldProperty(interfaces.IWebSite['title'])
    description = FieldProperty(interfaces.IWebSite['description'])
    keyword = FieldProperty(interfaces.IWebSite['keyword'])
    body = FieldProperty(interfaces.IWebSite['body'])

    def __init__(self, title=None):
        super(WebSite, self).__init__()
        if title is not None:
            self.title = title
        self.setSiteManager(site.LocalSiteManager(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class SiteConfigurator(configurator.ConfigurationPluginBase):
    """Configure the XPO site."""
    zope.component.adapts(interfaces.IWebSite)

    def __call__(self, data):
        # get parameters
    
        # Add the pluggable authentication utility
        sm = zope.component.getSiteManager(self.context)
        auth = SimpleAuthentication()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(auth))
        sm['default']['auth'] = auth
        sm.registerUtility(auth, IAuthentication)

        # setup credentials plugin
        cred = SessionCredentialsPlugin()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(cred))
        auth[u'credentials'] = cred
        auth.credentialsPlugins += (u'credentials',)

        prm = IPrincipalRoleManager(self.context)

        # setup 'members' member container
        members = MemberContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(members))
        auth[u'members'] = members
        auth.authenticatorPlugins += (u'members',)

        # setup 'groups' group container
        groups = GroupContainer(u'groups.')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(groups))
        auth[u'groups'] = groups
        auth.authenticatorPlugins += (u'groups',)

        # setup 'Members' group
        grp =  Group(u'Members', u'Members')
        groups.addGroup('Members', grp) 
        prm.assignRoleToPrincipal('z3c.website.Member', 'groups.Members')

        # setup 'Administrators' group
        grp =  Group(u'Administrators', u'Administrators')
        groups.addGroup('Administrators', grp) 
        prm.assignRoleToPrincipal('z3c.website.Administrator', 
            'groups.Administrators')

        # Add a Admin to the administrators group
        login = data['member.login']
        admin = Member(login, data['member.password'], data['member.title'], 
            data['member.description'])
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(admin))
        auth['members'].add(admin)

        adminGroup = groups['groups.Administrators']
        adminGroup.setPrincipals(
            adminGroup.principals + (admin.__name__,), check=False)

        # setup info top level folder
        info = page.Page()
        info.title = u'Info'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(info))
        self.context['info'] = info
        # create resource folder
        resource = IResource(info)
        configurator.configure(info, data)

        # setup tutorials top level folder
        tutorials = page.Page()
        tutorials.title = u'Tutorials'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(tutorials))
        self.context['tutorials'] = tutorials
        # create resource folder
        resource = IResource(tutorials)
        configurator.configure(tutorials, data)

        # setup contact top level folder
        download = page.Page()
        download.title = u'Download'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(download))
        self.context['download'] = download
        # create resource folder
        resource = IResource(download)
        configurator.configure(download, data)

        # setup contact top level folder
        contact = page.Page()
        contact.title = u'Contact'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(contact))
        self.context['contact'] = contact
        # create resource folder
        resource = IResource(contact)
        configurator.configure(contact, data)

        # setup samples folder
        samples = sample.Samples()
        samples.title = u'Samples'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(samples))
        self.context['samples'] = samples
        # create resource folder
        resource = IResource(samples)
        configurator.configure(samples, data)
