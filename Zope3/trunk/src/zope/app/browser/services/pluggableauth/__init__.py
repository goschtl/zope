##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Pluggable Authentication Service views.

$Id: __init__.py,v 1.5 2003/09/21 17:30:53 jim Exp $
"""

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.browser.container.adding import Adding
from zope.app.interfaces.services.pluggableauth import IPrincipalSource

class PrincipalSourceAdding(Adding):
    """Adding subclass used for principal sources."""

    menu_id = "add_principal_source"

    def add(self, content):

        if not IPrincipalSource.isImplementedBy(content):
            raise TypeError("%s is not a readable principal source" % content)

        return super(PrincipalSourceAdding, self).add(content)

class PrincipalAdd(BrowserView):

    def add(self, content):
        name = content.login
        self.context[name] = content
        return self.context[name]

    def nextURL(self):
        return "@@contents.html"

