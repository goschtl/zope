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
"""LDAP PAS Plugin interfaces

$Id$
"""

import re
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.interface import Interface
from zope.schema import TextLine

class ILDAPAuthentication(Interface):
    adapterName = TextLine(
        title=_("LDAP Adapter"),
        default=u'ldapadapter',
        required=True,
        )
    searchBase = TextLine(
        title=_("Search base"),
        default=u'dc=example,dc=org',
        required=True,
        )
    searchScope = TextLine(
        title=_("Search scope"),
        default=u'sub',
        required=True,
        )
    loginAttribute = TextLine(
        title=_("Login attribute"),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )
    principalIdPrefix = TextLine(
        title=_("Principal id prefix"),
        default=u'ldap.',
        required=False,
        )
    idAttribute = TextLine(
        title=_("Id attribute"),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )
    #searchObjectClasses
