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
"""/etc/passwd Authentication Plugin

This package defines a new authentication plugin, which can use textfiles to
authenticate users.

$Id$
"""
__docformat__ = 'restructuredtext'

import os
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.location import locate
from zope.app.pluggableauth import SimplePrincipal
from zope.app.pluggableauth.interfaces import ILoginPasswordPrincipalSource
from zope.app.security.interfaces import PrincipalLookupError
from zope.interface import implements
from interfaces import IFileBasedPrincipalSource

class PasswdPrincipalSource(Contained, Persistent):
    """A Principal Source for /etc/passwd-like files."""

    implements(ILoginPasswordPrincipalSource, IFileBasedPrincipalSource)

    def __init__(self, filename=''):
        self.filename = filename

    def readPrincipals(self):
        if not os.path.exists(self.filename):
            return []
        file = open(self.filename, 'r')
        principals = []
        for line in file.readlines():
            if line.strip() != '':
                user_info = line.strip().split(':', 3)
                p = SimplePrincipal(*user_info)
                locate(p, self, p._id)
                p._id = p.login
                principals.append(p)
        return principals

    def getPrincipal(self, id):
        """See `IPrincipalSource`."""
        earmark, source_name, id = id.split('\t')
        for p in self.readPrincipals():
            if p._id == id:
                return p
        raise PrincipalLookupError, id

    def getPrincipals(self, name):
        """See `IPrincipalSource`."""
        return filter(lambda p: p.login.find(name) != -1,
                      self.readPrincipals())

    def authenticate(self, login, password):
        """See `ILoginPasswordPrincipalSource`. """
        for user in self.readPrincipals():
            if user.login == login and user.password == password:
                return user
