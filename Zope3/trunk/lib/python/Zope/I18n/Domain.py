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
"""

$Id: Domain.py,v 1.5 2002/06/12 20:50:20 bwarsaw Exp $
"""

from Zope.I18n.IDomain import IDomain
from Zope.ComponentArchitecture import getServiceManager

class Domain:

    __implements__ =  IDomain

    def __init__(self, domain, service):
        self._domain = domain
        self._translationService = service

    def getDomainName(self):
        """Return the domain name"""
        return self._domain
    
    # IDomain interface methods

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None):
        """See Zope.I18n.IDomain.IDomain"""
        return self._translationService.translate(
            self._domain, msgid, mapping, context, target_language)
