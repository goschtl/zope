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
"""LDAP Adapter utility.

$Id$
"""

from zope.exceptions import NotFoundError

from zope.i18nmessageid import MessageIDFactory
_ = MessageIDFactory("ldapadapter")

from zope.schema._bootstrapinterfaces import ValidationError


class InvalidLDAPURI(ValidationError):
    __doc__ = _("""The specified LDAP URI is not valid.""")


# LDAP Adapter management errors

class LDAPURIParseError(Exception):
    """The given ldap uri is not valid."""

LDAP_uri_parse_error = _(u'The LDAP URI could not be parsed.')


# LDAP Adapter exceptions

class LDAPException(Exception):
    """LDAP exception"""

class ServerDown(LDAPException):
    """The server doesn't answer"""

class InvalidCredentials(LDAPException):
    """The credentials are incorrect"""

class NoSuchObject(LDAPException):
    """The base object doesn't exist"""
