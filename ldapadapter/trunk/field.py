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
"""LDAP Schema Fields

$Id: $
"""
import re

from zope.interface import implements

from zope.schema.interfaces import IURI
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import InvalidURI
from zope.schema import URI

from ldapadapter.exceptions import InvalidLDAPURI


_isldapuri = re.compile(
    r"^ldap[s]{0,1}://"           # protocol
    r"[a-zA-Z0-9\-\.]+"   # host
    r"[\:]{0,1}[\d]{0,5}"         # port
    ).match


class LDAPURI(URI):
    """LDAPURI schema field
    """

    implements(IURI, IFromUnicode)

    def _validate(self, value):
        """
        >>> from ldapadapter.field import LDAPURI
        >>> uri = LDAPURI(__name__='test')
        >>> uri.validate("ldap://www.python.org:389")
        >>> uri.validate("ldaps://www.python.org:389")
        >>> uri.validate("www.python.org")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: www.python.org
        
        >>> uri.validate("http://www.python.org")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: http://www.python.org
        
        >>> uri.validate("ldap://www.python.org/foo")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: ldap://www.python.org/foo
        
        """
        
        #super(LDAPURI, self)._validate(value)
        if _isldapuri(value):
            return

        raise InvalidLDAPURI, value

    def fromUnicode(self, value):
        """
        >>> from ldapadapter.field import LDAPURI
        >>> uri = LDAPURI(__name__='test')
        >>> uri.fromUnicode("ldap://www.python.org:389")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("ldaps://www.python.org:389")
        'ldaps://www.python.org:389'
        >>> uri.fromUnicode("          ldap://www.python.org:389")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("      \\n    ldap://www.python.org:389\\n")
        'ldap://www.python.org:389'
        >>> uri.fromUnicode("ldap://www.pyt hon.org:389")
        Traceback (most recent call last):
        ...
        InvalidLDAPURI: ldap://www.pyt hon.org:389
        """
        v = str(value.strip())
        self.validate(v)
        return v
