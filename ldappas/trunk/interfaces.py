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
from zope.schema import Choice
from zope.schema import TextLine

class ILDAPAuthentication(Interface):
    adapterName = Choice(
        title=_(u"LDAP Adapter Name"),
        description=_(u"The LDAP adapter name for the connection to be used."),
        vocabulary="LDAP Adapter Names",
        required=True,
        )
    searchBase = TextLine(
        title=_("Search base"),
        description=_(u"The LDAP search base where principals are found."),
        default=u'dc=example,dc=org',
        required=True,
        )
    searchScope = TextLine(
        title=_("Search scope"),
        description=_(u"The LDAP search scope used to find principals."),
        default=u'sub',
        required=True,
        )
    loginAttribute = TextLine(
        title=_("Login attribute"),
        description=_(u"The LDAP attribute used to find principals."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )
    principalIdPrefix = TextLine(
        title=_("Principal id prefix"),
        description=_(u"The prefix to add to all principal ids."),
        default=u'ldap.',
        required=False,
        )
    idAttribute = TextLine(
        title=_("Id attribute"),
        description=_(u"The LDAP attribute used to determine principal ids."),
        constraint=re.compile("[a-zA-Z][-a-zA-Z0-9]*$").match,
        default=u'uid',
        required=True,
        )
    #searchObjectClasses
