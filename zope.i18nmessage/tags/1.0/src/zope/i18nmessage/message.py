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
"""i18n messages
"""

class Message(unicode):

    __slots__ = ('domain', 'context', 'mapping')

    def __new__(cls, ustr, domain=None, context=None, mapping=None):
        self = unicode.__new__(cls, ustr)
        if isinstance(ustr, self.__class__):
            domain = ustr.domain and ustr.domain[:] or domain
            context = ustr.context and ustr.context[:] or context
            mapping = ustr.mapping and ustr.mapping.copy() or mapping
            ustr = unicode(ustr)
        self.domain = domain
        self.context = context
        self.mapping = mapping
        return self

    def __reduce__(self):
        return self.__class__, self.__getstate__()

    def __getstate__(self):
        return unicode(self), self.domain, self.context, self.mapping


class MessageFactory(object):
    """Factory for creating i18n messages."""

    def __init__(self, domain):
        self._domain = domain

    def __call__(self, ustr, context=None, mapping=None):
        return Message(ustr, self._domain, context, mapping)
