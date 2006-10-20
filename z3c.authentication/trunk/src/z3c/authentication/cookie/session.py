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

import zope.interface
from zope.app.session.session import PersistentSessionDataContainer
from z3c.authentication.cookie import interfaces


class CookieCredentialSessionDataContainer(PersistentSessionDataContainer):
    """A persistent cookie credential container."""

    zope.interface.implements(
        interfaces.ICookieCredentialSessionDataContainer)

    def __init__(self):
        super(CookieCredentialSessionDataContainer, self).__init__()
        self.timeout = 1 * 60 * 60 * 24 * 365
