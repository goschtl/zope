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

$Id: __init__.py,v 1.4 2003/07/10 09:27:40 alga Exp $
"""
from zope.app.browser.services.service import Adding
from zope.context import ContextSuper
from zope.app.interfaces.services.pluggableauth import IPrincipalSource

class PrincipalSourceAdding(Adding):
    """Adding subclass used for principal sources."""

    menu_id = "add_principal_source"

    def add(self, content):

        if not IPrincipalSource.isImplementedBy(content):
            raise TypeError("%s is not a readable principal source" % content)

        return ContextSuper(PrincipalSourceAdding, self).add(content)
