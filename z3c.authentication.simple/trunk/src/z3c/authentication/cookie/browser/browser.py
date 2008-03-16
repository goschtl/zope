##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
$Id$
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.formlib import form
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.session.interfaces import ISessionDataContainer
from z3c.i18n import MessageFactory as _
from z3c.authentication.cookie import interfaces
from z3c.authentication.cookie import session


class CookieCredentialSessionDataContainerAddForm(form.AddForm):
    """CookieCredentialSessionDataContainer add form choosing the right 
    session data container name."""

    label = _('Add Cookie Credential Data Container')
    template = ViewPageTemplateFile('add.pt')

    form_fields = form.Fields(
        zope.schema.TextLine(__name__='__name__', title=_(u"Object Name"),
            required=True, default=unicode(interfaces.SESSION_KEY)))

    def create(self, data):
        return session.CookieCredentialSessionDataContainer()

    def add(self, obj):
        name = self.request.get('__name__', None) or interfaces.SESSION_KEY
        self.context.contentName = name 
        self.context.add(obj)
        sm = zope.component.getSiteManager(self.context)
        sm.registerUtility(obj, ISessionDataContainer, 
            name=interfaces.SESSION_KEY)
        self._finished_add = True
        return obj

