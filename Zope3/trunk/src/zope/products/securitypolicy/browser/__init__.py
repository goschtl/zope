##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
""" Define view component for service manager contents.

$Id: __init__.py,v 1.2 2004/01/14 22:55:33 chrism Exp $
"""
from zope.app.browser.container.contents import Contents
from zope.products.securitypolicy.role import Role, ILocalRoleService

class Add:
    "Provide a user interface for adding a role"
    __used_for__ = ILocalRoleService

    def action(self, id, title, description):
        "Add a contact"
        role = Role(id, title, description)
        self.context[id] = role
        self.request.response.redirect('.')


class Contents(Contents):
    # XXX: What the heck is that? I guess another dead chicken.
    pass
