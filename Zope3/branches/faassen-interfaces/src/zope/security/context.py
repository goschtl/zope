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
"""Default 'ISecurityContext' implementation.

$Id: context.py,v 1.5 2004/02/20 20:42:12 srichter Exp $
"""
from zope.security.interfaces import ISecurityContext
from zope.interface import implements

class SecurityContext:
    """Capture transient request-specific security information.

    Attribute('stack',
              'A stack of elements, each either be an ExecutableObject or a'
              ' tuple consisting of an ExecutableObject and a custom'
              ' SecurityPolicy.'
              )

    Attribute('user',
              'The AUTHENTICATED_USER for the request.'
              )
    """
    implements(ISecurityContext)

    def __init__(self, user):
        self.stack       = []
        self.user        = user
        self.objectCache = {}
