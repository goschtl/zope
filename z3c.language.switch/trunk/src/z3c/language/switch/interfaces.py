##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
from zope.schema.interfaces import IVocabularyTokenized


class IReadI18n(zope.interface.Interface):
    """Let the language switch to the desired language.
    
    Support add and remove objects of a language.
    """

    def getDefaultLanguage():
        """Return the default language."""

    def getPreferedLanguage():
        """Return the best matching language."""

    def getAvailableLanguages():
        """Find all the languages that are available."""

    def getAttribute(name, language=None):
        """Get name attribute of the language specific translation.

        Parameter:

        name -- Attribute name.

        language -- Language code for example 'de'. If None the default language
        is returned.

        Return Value:

        object -- Evaluate of the language specific data object.

        Exceptions:

        KeyError -- If attribute or language code does not exists.

        """

    def queryAttribute(name, language=None, default=None):
        """Get name attribute of the language specific translation or default.

        Parameter:

        name -- Attribute name.

        language -- Language code for example 'de'. If None the default language
        is returned.

        default -- Any object.

        Return Value:

        object -- Evaluate of the language specific data object or return default
        if not found.

        """


class IWriteI18n(zope.interface.Interface):
    """Let the language switch to the desired language.
    
    Support add and remove objects of a language.
    """

    def setDefaultLanguage(language):
        """Set the default language, which will be used if the language is not
        specified, or not available.
        """

    def addLanguage(language, *args, **kw):
        """Add a i18n base object of the i18n type. The ``*args``, ``**kw`` 
        can be used for the constructor of a new sub object.
        """

    def removeLanguage(language):
        """Remove the object under the given language."""

    def setAttributes(language, **kws):
        """Set the language specific attribute of the translation defined by kw.

        Parameter:

        language -- Language code for example ``'de'``

        kws -- Attributes that have to be set as keyword value pairs.

        Exceptions:

        KeyError -- If attribute does not exists.
        
        """


class II18n(IReadI18n, IWriteI18n):
    """Read and write support for I18n objects."""


class II18nLanguageSwitch(zope.interface.Interface):
    """Let the language switch to the desired language."""

    def getLanguage():
        """Returns the used language."""

    def setLanguage(language):
        """Sets the language for useing in the adapter."""


class IAvailableLanguages(zope.interface.Interface):

    def getAvailableLanguages():
        """Returns a list of available languages if we provide IReadI18n."""

    def hasAvailableLanguages():
        """View for to check if we have i18n support on a context."""


class IAvailableLanguagesVocabulary(IVocabularyTokenized):
    """Available languages."""

