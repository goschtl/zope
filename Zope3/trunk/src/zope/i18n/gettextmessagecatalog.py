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
"""A simple implementation of a Message Catalog.

$Id: gettextmessagecatalog.py,v 1.9 2003/08/12 19:11:11 srichter Exp $
"""

from pythonlib.gettext import GNUTranslations
from zope.i18n.interfaces import IGlobalMessageCatalog
from zope.interface import implements


class _KeyErrorRaisingFallback:
    def ugettext(self, message):
        raise KeyError, message


class GettextMessageCatalog:
    """A message catalog based on GNU gettext and Python's gettext module."""

    implements(IGlobalMessageCatalog)

    def __init__(self, language, domain, path_to_file):
        """Initialize the message catalog"""
        self._language = language
        self._domain = domain
        self._path_to_file = path_to_file
        self.reload()

    def reload(self):
        'See IMessageCatalog'
        fp = open(self._path_to_file, 'r')
        try:
            self._catalog = GNUTranslations(fp)
        finally:
            fp.close()

    def getMessage(self, id):
        'See IMessageCatalog'
        return self._catalog.ugettext(id)

    def queryMessage(self, id, default=None):
        'See IMessageCatalog'
        try:
            return self._catalog.ugettext(id)
        except KeyError:
            return default

    def getLanguage(self):
        'See IMessageCatalog'
        return self._language

    def getDomain(self):
        'See IMessageCatalog'
        return self._domain

    def getIdentifier(self):
        'See IMessageCatalog'
        return self._path_to_file
