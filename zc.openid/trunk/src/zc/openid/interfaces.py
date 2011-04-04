##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

from zope.app.security.interfaces import IAuthentication
from zope.interface import Interface
from zope.schema import URI

class IOpenIDConsumerConfig(Interface):
    single_provider = URI(
        title=u'Single Identity Provider URI',
        description=(u'If you want all identities to come from a single '
                     u'provider, set this to the server URI.  The '
                     u'URI must contain an OpenID service description.'),
        required=False
        )


class IOpenIDConsumer(IOpenIDConsumerConfig, IAuthentication):
    pass

class AuthenticationFailed(Exception):
    """OpenID authentication failed"""
