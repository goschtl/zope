##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
from zope.interface.common.mapping import IMapping
from zope.interface import Interface

class IOptionDictRead(Interface):
    """Option dictionary read interface."""

    def getLanguages():
        """Return available languages."""

    def getDefaultKey():
        """Return default key."""

    def getKeys():
        """Return available keys."""

    def queryValue(key, language, default=None):
        """Return value for key/language pair."""

    def getValue(key, language):
        """Return value for key/language pair."""

class IOptionDictWrite(Interface):
    """Option dictionary write interface."""

    def setDefaultKey(key):
        """Change default key."""

    def addValue(key, language, value):
        """Add value for a key/language pair."""

    def delValue(key, language):
        """Delete value for a key/language pair."""

    def delAllValues():
        """Delete all values."""

class IOptionDict(IOptionDictRead,IOptionDictWrite):
    """Option dictionary."""

class IOptionStorage(IMapping):
    """Option storage, mapping names to option dictionaries."""

class IOptionStorageVocabulary(Interface):

    def getDefaultKey():
        """Return default key for an option storage vocabulary."""

