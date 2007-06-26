##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""HTTP Referer Credentials interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.schema
from zope.app.authentication import interfaces

class IHTTPRefererCredentials(interfaces.ICredentialsPlugin):
    """HTTP-Referer Credentials"""

    sessionKey = zope.schema.ASCIILine(
        title=u'Session Key',
        description=u'Session Key')

    allowedHosts = zope.schema.Tuple(
        title=u'Allowed Hosts',
        description=u'A list of hosts allowed to access.',
        default=('localhost',))

    credentials = zope.schema.Field(
        title=u'Credentials',
        description=(u'An object representing the credentials of the '
                     u'referred user.'))

    challengeView = zope.schema.TextLine(
        title=u'Challenge View',
        description=(u'The view to which the user is forwarded when not '
                     u'coming from a correct referer site.'),
        default=u'unauthorized.html')
