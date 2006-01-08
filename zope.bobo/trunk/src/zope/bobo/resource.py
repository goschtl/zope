##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Resource base class

$Id$
"""

import zope.interface
from zope.publisher.interfaces.browser import IBrowserPublisher
import zope.security.checker

class PublicResource(object):

    __Security_checker__ = zope.security.checker.NamesChecker(
        ('publishTraverse', 'browserDefault', '__call__'))

    zope.interface.implements(IBrowserPublisher)

    def __init__(self, request):
        self.request = request

    def publishTraverse(self, request, name):
        ob = getattr(self, name, None)
        if not IBrowserPublisher.providedBy(ob):
            raise zope.publisher.interfaces.NotFound(self, name)

    def browserDefault(self, request):
        return self, ()

    
