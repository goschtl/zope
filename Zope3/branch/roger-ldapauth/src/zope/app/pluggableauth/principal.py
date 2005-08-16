##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Pluggable Authentication service implementation.

$Id: principal.py 26176 2004-07-07 18:34:31Z jim $
"""
from warnings import warn
from persistent import Persistent
from zope.interface import implements
from zope.app.container.contained import Contained
from interfaces import IUserSchemafied
from interfaces import IPrincipalSourceContained



class SimplePrincipal(Persistent, Contained):
    """A no-frills IUserSchemafied implementation."""

    implements(IUserSchemafied, IPrincipalSourceContained)

    def __init__(self, login, password, title='', description=''):
        self._id = ''
        self.login = login
        self.password = password
        self.title = title
        self.description = description

    def _getId(self):
        source = self.__parent__
        auth = source.__parent__
        return "%s\t%s\t%s" %(auth.earmark, source.__name__, self._id)

    def _setId(self, id):
        self._id = id

    id = property(_getId, _setId)

    def getTitle(self):
        warn("Use principal.title instead of principal.getTitle().",
             DeprecationWarning, 2)
        return self.title

    def getDescription(self):
        warn("Use principal.description instead of principal.getDescription().",
             DeprecationWarning, 2)
        return self.description

    def getLogin(self):
        """See IReadUser."""
        return self.login

    def validate(self, test_password):
        """ See IReadUser.

        >>> pal = SimplePrincipal('gandalf', 'shadowfax', 'The Grey Wizard',
        ...                       'Cool old man with neato fireworks. '
        ...                       'Has a nice beard.')
        >>> pal.validate('shdaowfax')
        False
        >>> pal.validate('shadowfax')
        True
        """
        return test_password == self.password


