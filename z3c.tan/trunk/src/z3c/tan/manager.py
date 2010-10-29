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
"""TAN Manager Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent.list
import zope.component
import zope.interface
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IQuerySchemaSearch
from zope.app.authentication.interfaces import IAuthenticatedPrincipalCreated
from zope.app.authentication import principalfolder
from zope.app.container import btree

from z3c.tan import interfaces, session


class TANManager(btree.BTreeContainer):
    zope.interface.implements(
        interfaces.ITANManager, IAuthenticatorPlugin, IQuerySchemaSearch)

    schema = principalfolder.ISearchSchema

    def __init__(self, prefix=u''):
        super(TANManager, self).__init__()
        self.prefix = prefix
        self._usedTANs = persistent.list.PersistentList()

    def __setitem__(self, key, value):
        """See zope.app.container.interfaces.IContainer"""
        if value.tan in self._usedTANs:
            raise interfaces.TANAlreadyUsed(value.tan)
        self._usedTANs.append(value.tan)
        super(TANManager, self).__setitem__(key, value)

    def add(self, tan):
        """See interfaces.ITANManager"""
        self.__setitem__(tan.tan, tan)

    def authenticateCredentials(self, credentials):
        """See zope.app.authentication.interfaces.IAuthenticatorPlugin"""
        if not isinstance(credentials, basestring):
            return None
        if credentials not in self:
            return None
        return self.principalInfo(self.prefix+credentials)

    def principalInfo(self, id):
        """See zope.app.authentication.interfaces.IAuthenticatorPlugin"""
        if not id.startswith(self.prefix):
            return None
        id = id[len(self.prefix):]
        if id not in self:
            return None
        internal = self[id]
        clone = internal.__class__.__new__(internal.__class__)
        clone.__dict__.update(internal.__dict__)
        clone.id = self.prefix + clone.id
        zope.interface.directlyProvides(clone, IPrincipalInfo)
        return clone

    def search(self, query, start=None, batch_size=None):
        """See zope.app.authentication.interfaces.IQuerySchemaSearch"""
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        n = 1
        for i, value in enumerate(self.values()):
            if ((value.title and search in value.title.lower()) or
                (value.description and search in value.description.lower()) or
                search in value.tan.lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield self.prefix + value.tan


@zope.component.adapter(IAuthenticatedPrincipalCreated)
def assignTAN(event):
    """Assign a TAN as group to a principal."""
    credentials = session.SessionCredentialsPlugin()
    tan = credentials.extractCredentials(event.request)
    if tan is None:
        return
    elif event.principal.id.endswith(tan):
        # The principal is the TAN
        return
    # Look in the plugins for TAN managers and assign the TAN
    for pluginName in event.authentication.authenticatorPlugins:
        plugin = event.authentication[pluginName]
        if not interfaces.ITANManager.providedBy(plugin):
            continue
        tanInfo = plugin.get(tan)
        if tanInfo is None:
            continue
        # The principal is not allowed to use that TAN
        if (tanInfo.allowedPrincipals is not None and
            event.principal.id not in tanInfo.allowedPrincipals):
            return
        event.principal.groups.append(event.authentication.prefix + tan)
