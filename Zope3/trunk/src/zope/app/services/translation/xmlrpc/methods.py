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

$Id: methods.py,v 1.4 2003/06/06 21:21:47 stevea Exp $
"""
from zope.proxy import removeAllProxies

from zope.publisher.xmlrpc import XMLRPCView


class Methods(XMLRPCView):

    def getAllDomains(self):
        return self.context.getAllDomains()

    def getAllLanguages(self):
        return self.context.getAllLanguages()

    def getMessagesFor(self, domains, languages):
        messages = []
        for domain in domains:
            for msg in self.context.getMessagesOfDomain(domain):
                if msg['language'] in languages:
                    messages.append(removeAllProxies(msg))

        return messages
