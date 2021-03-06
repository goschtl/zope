##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""
Dummy TALES engine so that I can test out the TAL implementation.

BBB 2005/05/01 -- to be removed after 12 months
"""
import zope.deprecation
zope.deprecation.moved('zope.tal.dummyengine', '2.12')

from zope.tal.dummyengine import DummyTranslationDomain as DummyDomain

class DummyTranslationService:

    def translate(self, domain, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        return self.getDomain(domain).translate(msgid, mapping, context,
                                                target_language,
                                                default=default)

    def getDomain(self, domain):
        return DummyDomain()
