##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""A plugable authentication module for LDAP.

$Id:
"""

import ldap
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.pluggableauth.interfaces import \
        ILoginPasswordPrincipalSource, IContainerPrincipalSource
from zope.app.location import locate
from zope.app.pluggableauth import SimplePrincipal
from zope.exceptions import NotFoundError
from zope.interface import implements

from interfaces import ILDAPBasedPrincipalSource

class LDAPPrincipalSource(Contained, Persistent):
    """A Principal source using LDAP"""
    implements(ILoginPasswordPrincipalSource, ILDAPBasedPrincipalSource,
            IContainerPrincipalSource)

    def __init__(self, server=u'', port=389, basedn=u'',
            login_attribute=u'',
            manager_dn=u'', manager_passwd=u''):
        self.host = server
        self.port = port
        self.basedn = basedn
        self.login_attribute = login_attribute
        self.manager_dn = manager_dn
        self.manager_passwd = manager_passwd
    
    ### IContainer-related methods

    def __delitem__(self, login):
        pass

    # XXX We should use setitem from zope.app.container.contained
    # Would allow events and so on. This is just a test.
    # This way of registering the principal is somehow stupid since we must
    # use it each time a new principal is created. This is UGLY.
    def __setitem__(self, login, obj):
        obj.id = login
        obj.__parent__ = self

    def keys(self):
        pass

    def __iter__(self):
        pass

    def __getitem__(self):
        pass

    def get(self, key, default=None):
        pass

    def values(self):
        pass

    def __len__(self):
        pass
    
    def items(self):
        pass

    def __contains__(self):
        pass
    
    ### IPrincipalSource methods
    
    def getPrincipal(self, id):
        uid = id.split('\t')[2]
        l = self.__connect()
        l.simple_bind_s(self.manager_dn, self.manager_passwd)
        lsearch = l.search_s(self.basedn, ldap.SCOPE_ONELEVEL,
                '(%s=%s)' % (self.login_attribute, uid))
        if lsearch:
            uid_dn, uid_dict = lsearch[0]
            principal = SimplePrincipal(
                    login = uid_dict[self.login_attribute][0],
                    password = uid_dict['userPassword'][0])
            self.__setitem__(principal.login, principal)
            return principal
        else:
            raise NotFoundError, id

    def getPrincipals(self, name):
        if name == '' :
            search = '(%s=*)' % self.login_attribute
        else:
            search = '(%s=*%s*)' % (self.login_attribute, name)
        l = self.__connect()
        l.simple_bind_s(self.manager_dn, self.manager_passwd)
        lsearch = l.search_s(self.basedn, ldap.SCOPE_ONELEVEL, search)
        
        principals = []
        for userinfo in lsearch:
            uid_dn, uid_dict = userinfo
            principal = SimplePrincipal(
                    login = uid_dict[self.login_attribute][0],
                    password = uid_dict['userPassword'][0])
            self.__setitem__(principal.login, principal)
            principals.append(principal)

        return principals

    def authenticate(self, uid, password):
        if password:
            l = self.__connect()
            dn = '%s=%s,' % (self.login_attribute, uid) + self.basedn
            try:
                l.simple_bind_s(dn, password)
                principal = SimplePrincipal(login = uid, password = password)
                self.__setitem__(uid, principal)
                return principal
            except ldap.INVALID_CREDENTIALS:
                return None
        else:
            return None

    def __connect(self):
        conn = getattr(self, '_v_conn', None)
        if not conn:
            connectstring = 'ldap://%s:%s' % (self.host, self.port)
            connection = ldap.initialize(connectstring)
            self._v_conn = connection
            return connection
        else:
            return conn
            
