##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""A LDAP user for the ldapauth plugable authentication module.

$Id$
"""

from zope.interface import implements

from zope.app.container.contained import Contained
from zope.app.security.interfaces import IPrincipal

class LDAPPrincipal(Contained):
    """A really simple implemantation of the principal interface"""

    implements(IPrincipal)

    def __init__(self, login):
        self._id = login
        self.login = login
        self.title = ''
        self.description = ''

    def _getId(self):
        source = self.__parent__
        auth = source.__parent__
        return "%s\t%s\t%s" % (auth.earmark, source.__name__, self._id)

    def _setId(self, id):
        self._id = id

    id = property(_getId, _setId)
