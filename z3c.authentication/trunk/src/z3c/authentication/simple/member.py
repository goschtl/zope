###############################################################################
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
###############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import md5
import random
import time
import socket
import persistent
import zope.interface
import zope.component
from zope.app.container import contained
from zope.app.container import btree
from zope.app.container.interfaces import DuplicateIDError
from zope.app.authentication.interfaces import IPasswordManager

from z3c.authentication.simple import interfaces

# get the IP addresss only once
try: 
  ip = socket.getaddrinfo(socket.gethostname(), 0)[-1][-1][0]
except:
  ip = '127.0.0.1'

def generateUserIDToken(id):
    """Generates a unique user id token."""
    t = long(time.time() * 1000)
    r = long(random.random()*100000000000000000L)
    data = str(ip)+' '+str(t)+' '+str(r)+' '+str(id)
    return md5.md5(data).hexdigest()


class Member(persistent.Persistent, contained.Contained):
    """User stored in IMemberContainer."""

    zope.interface.implements(interfaces.IMember)

    def __init__(self, login, password, title, description=u'',
            passwordManagerName="Plain Text"):
        self._login = login
        self._passwordManagerName = passwordManagerName
        self.password = password
        self.title = title
        self.description = description

    def getPasswordManagerName(self):
        return self._passwordManagerName

    passwordManagerName = property(getPasswordManagerName)

    def _getPasswordManager(self):
        return zope.component.getUtility(IPasswordManager, 
            self.passwordManagerName)

    def getPassword(self):
        return self._password

    def setPassword(self, password, passwordManagerName=None):
        if passwordManagerName is not None:
            self._passwordManagerName = passwordManagerName
        passwordManager = self._getPasswordManager()
        self._password = passwordManager.encodePassword(password)

    password = property(getPassword, setPassword)

    def checkPassword(self, password):
        passwordManager = self._getPasswordManager()
        return passwordManager.checkPassword(self.password, password)

    def getLogin(self):
        return self._login

    def setLogin(self, login):
        oldLogin = self._login
        self._login = login
        if self.__parent__ is not None:
            try:
                self.__parent__.notifyLoginChanged(oldLogin, self)
            except ValueError:
                self._login = oldLogin
                raise

    login = property(getLogin, setLogin)


class MemberContainer(btree.BTreeContainer):
    """A Persistent Member Container and authenticator plugin.

    See principalfolder.txt for details.
    """

    zope.interface.implements(interfaces.IMemberContainer, 
        interfaces.IQuerySchemaSearch)

    schema = interfaces.IMemberSearchCriteria

    def __init__(self):
        super(MemberContainer, self).__init__()
        self.__id_by_login = self._newContainerData()

    def notifyLoginChanged(self, oldLogin, principal):
        """Notify the Container about changed login of a principal.

        We need this, so that our second tree can be kept up-to-date.
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError('Principal Login already taken!')

        del self.__id_by_login[oldLogin]
        self.__id_by_login[principal.login] = principal.__name__

    def __setitem__(self, id, member):
        """Add a IPrincipal object within a correct id.

        Create a MemberContainer

        >>> mc = MemberContainer('members.')

        Try to add something not providing IMember
        >>> try:
        ...     mc.__setitem__(u'max', object())
        ... except Exception, e:
        ...     print e
        Item does not support IMember!

        Create a member with no __name__, this should be added via the add
        method

        >>> member = Member()
        >>> try:
        ...     mc.__setitem__(u'max', member)
        ... except Exception, e:
        ...     print e
        There is no user id token given!

        Probabl we do hav a __name__ during copy/paste, so we have to check 
        if we get a __parent__ as well 

        >>> member = Member()
        >>> member.__name__ = u'usertoken'
        >>> try:
        ...     mc.__setitem__(u'max', member)
        ... except Exception, e:
        ...     print e
        Paste a object is not supported!

        Try to use a member with no login:

        >>> try:
        ...     mc.__setitem__(u'max', member)
        ... except Exception, e:
        ...     print e
        Member does not provide a login value!

        Add a login attr since __setitem__ is in need of one

        >>> member.login = u'max'
        >>> mc.__setitem__(u'members.max', principal)

        Now try to use the same login:

        >>> try:
        ...     mc.__setitem__(u'max', member)
        ... except Exception, e:
        ...     print e
        Login already taken!
        """

        # check if we store correct implementations
        if not interfaces.IMember.providedBy(member):
            raise TypeError('Item does not support IMember!')

        # check if there is a user id given
        if member.__name__ is not id:
            raise ValueError('There is no user id token given!')

        # check if there is a user id given in we store correct implementations
        if member.__parent__ is not None:
            raise ValueError('Paste a object is not supported!')

        # The member doesn't provide a login
        if not member.login:
            raise ValueError('Member does not provide a login value!')

        # A user with the new login already exists
        if member.login in self.__id_by_login:
            raise DuplicateIDError('Login already taken!')

        super(MemberContainer, self).__setitem__(id, member)
        self.__id_by_login[member.login] = id

    def add(self, member):
        token = generateUserIDToken(member.login)
        # Pre set the user id like a ticket, so we can check it in __setitem__
        member.__name__ = token
        self[token] = member
        return token, self[token]

    def __delitem__(self, id):
        """Remove principal information."""
        member = self[id]
        super(MemberContainer, self).__delitem__(id)
        del self.__id_by_login[member.login]

    def authenticateCredentials(self, credentials):
        """Return principal if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        id = self.__id_by_login.get(credentials['login'])
        if id is None:
            return None
        member = self[id]
        if not member.checkPassword(credentials["password"]):
            return None
        return member

    def queryPrincipal(self, id, default=None):
        member = self.get(id)
        if member is not None:
            return member
        return default

    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider."""
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        n = 1
        for i, value in enumerate(self.values()):
            if (search in value.title.lower() or
                search in value.description.lower() or
                search in value.login.lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield value.__name__
