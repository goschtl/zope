##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""securityPolicy Directive Schema

$Id: metadirectives.py,v 1.1 2003/08/02 20:05:30 srichter Exp $
"""
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

class ISecurityPolicyDirective(Interface):
    """Defines the security policy that will be used for Zope."""

    component = GlobalObject(
        title=u"Component",
        description=u"Pointer to the object that will handle the security.",
        required=True)
