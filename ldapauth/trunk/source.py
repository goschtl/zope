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
from zope.app.container.contained import Contained, setitem
from zope.app.pluggableauth.interfaces import \
        ILoginPasswordPrincipalSource, IContainerPrincipalSource
from zope.app.location import locate
from zope.app.pluggableauth import SimplePrincipal
from zope.exceptions import NotFoundError
from zope.interface import implements

from zope.app.cache.ram import RAMCache
from zope.app.cache.caching import getCacheForObject, getLocationForCache
from zope.app.cache.annotationcacheable import AnnotationCacheable

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
        cache = getCacheForObject(self)
        location = getLocationForCache(self)
        if cache and location:
            cache.invalidate(location, login)

    ### This is the stuff needed to add the Principal to the cache and to
    ### make it containment friendly.
    ### TODO: add the principal to the ldap server if it is a new one.
    def __setitem__(self, login, obj):
        obj.id = login
        setitem(self, self._setitem, login, obj)

    def _setitem(self, key, obj):
        cache = getCacheForObject(self)
        location = getLocationForCache(self)
        if cache and location:
            principal = cache.query(location, key)
            if principal is None:
                cache.set(obj, location, key)

    def keys(self):
        logins = []
        l = self.__connect()
        l.simple_bind_s(self.manager_dn, self.manager_passwd)
        lsearch = l.search_s(self.basedn, ldap.SCOPE_ONELEVEL, '(%s=*)' %
                self.login_attribute)
        for node in lsearch:
            node_dn, node_dict = node
            logins.append(node_dict[self.login_attribute][0])
        return logins

    def __iter__(self):
        return self.keys()

    def __getitem__(self, key):
        cache = getCacheForObject(self)
        location = getLocationForCache(self)
        if cache and location:
            principal = cache.query(location, key)
            if principal is None:
                principal = self.__findInLDAP(key)
            
                #XXX 
                # RuntimeError: maximum recursion depth exceeded
                # this is calling __setitem__ if we call authenticate --> __setitem__ --> __getitem__ --> ...

                #self[principal.login] = principal
        else:
            principal = self.__findInLDAP(key)
            
            #XXX 
            # RuntimeError: maximum recursion depth exceeded
            # this is calling __setitem__ if we call authenticate --> __setitem__ --> __getitem__ --> ...
            
            #self[principal.login] = principal
        return principal

    def __findInLDAP(self, login):
        l = self.__connect()
        l.simple_bind_s(self.manager_dn, self.manager_passwd)
        lsearch = l.search_s(self.basedn, ldap.SCOPE_ONELEVEL,
                '(%s=%s)' % (self.login_attribute, login))
        if lsearch:
            uid_dn, uid_dict = lsearch[0]
            principal = SimplePrincipal(
                    login = uid_dict[self.login_attribute][0],
                    password = uid_dict['userPassword'][0])
            return principal

    def get(self, key, default=None):
        return self[key]

    def values(self):
        pass

    def __len__(self):
        pass
    
    def items(self):
        pass

    def __contains__(self, key):
        pass
    
    ### IPrincipalSource methods
    
    def getPrincipal(self, id):
        uid = id.split('\t')[2]
        principal = self[uid]
        if principal:
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
        for node in lsearch:
            node_dn, node_dict = node
            principal = SimplePrincipal(
                    login = node_dict[self.login_attribute][0],
                    password = node_dict['userPassword'][0])
            self[principal.login] = principal
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
            
