##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""ZSCP Web Site

$Id$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty

from zope.app import folder
from zope.app import security
from zope.app.authentication import principalfolder
from zope.app.authentication import authentication
from zope.app.component import site

from zf.zscp.website import interfaces


class ZSCPSite(folder.folder.Folder):
    zope.interface.implements(interfaces.IZSCPSite)

    def __init__(self):
        super(ZSCPSite, self).__init__()
        self.setSiteManager(site.LocalSiteManager(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


_marker = object()


def addAuthenticationUtilityToSite(ob, event):
    """Add a pluggable authentication utility to the zscp site."""
    sm = ob.getSiteManager()
    prefix = 'zscp.'

    pau = authentication.PluggableAuthentication()
    sm['default']['pau'] = pau
    sm.registerUtility(pau, security.interfaces.IAuthentication)

    # setup 'principals' principal folder
    principals = principalfolder.PrincipalFolder(prefix)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(principals))
    pau['principals'] = principalfolder.PrincipalFolder()
    pau.authenticatorPlugins += (u'principals',)

