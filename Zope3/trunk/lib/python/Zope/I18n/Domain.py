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

$Id: Domain.py,v 1.2 2002/06/10 23:29:27 jim Exp $
"""

from Zope.I18n.IDomain import IDomain

class Domain:

    __implements__ =  IDomain

    def __init__(self, place, domain):
        self._place = place
        self.domain = domain


    def getPlace(self):
        """Return the place this domain was created for."""
        return self._place


    def getDomainName(self):
        """Return the domain name"""
        return self._domain
    

    ############################################################
    # Implementation methods for interface
    # IDomain.py

    def translate(self, source, mapping=None, context=None,
                  target_language=None):
        'See Zope.I18n.IDomain.IDomain'

        # lookup the correct translation service
        service_manager = getServiceManager(self.place)
        service = service_manager.getBoundService('Translation Service')

        return service.translate(self.domain, source, mapping, context,
                                 target_language)

    #
    ############################################################
