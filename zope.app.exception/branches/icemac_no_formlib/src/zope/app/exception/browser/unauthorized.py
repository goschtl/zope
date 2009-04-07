##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unauthorized Exception View Class

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.authentication.interfaces import IAuthentication
from zope.publisher.browser import BrowserPage
from zope.formlib import namedtemplate
import zope.component
from zope.app.pagetemplate import ViewPageTemplateFile
import z3c.template.interfaces

class Unauthorized(BrowserPage):

    def __call__(self):
        # Set the error status to 403 (Forbidden) in the case when we don't
        # challenge the user
        self.request.response.setStatus(403)

        # make sure that squid does not keep the response in the cache
        self.request.response.setHeader('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
        self.request.response.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.request.response.setHeader('Pragma', 'no-cache')

        principal = self.request.principal
        auth = zope.component.getUtility(IAuthentication)
        auth.unauthorized(principal.id, self.request)
        if self.request.response.getStatus() not in (302, 303):
            template = zope.component.getMultiAdapter(
                (self, self.request), z3c.template.interfaces.IContentTemplate,
                name='default')
            return template(self)
