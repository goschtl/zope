##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
    identity_provider = URI(
        title=u'Identity Provider URI',
        required=False
        )

class IOpenIDConsumer(IOpenIDConsumerConfig, IAuthentication):
    pass

class AuthenticationFailed(Exception):
    """OpenID authentication failed"""
