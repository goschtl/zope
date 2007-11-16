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

from z3c.language.switch import II18n
from z3c.language.switch import II18nLanguageSwitch


class I18nLanguageSwitch(object):
    """Mixing class for switch a language on a object.
    
    Use the method _getI18n for set the i18n object.
    """
    zope.interface.implements(II18nLanguageSwitch)

    _language = 'en'

    def __init__(self, context):
        self.context = context
        self.i18n = self._getI18n()
        self._language = self._getDefaultLanguage()

    def _getDefaultLanguage(self):
        """Subclasses may overwrite this method."""
        return self.i18n.getDefaultLanguage()

    def _getI18n(self):
        """Subclasses may overwrite this method."""
        return self.context

    # II18nLanguageSwitch interface
    def getLanguage(self):
        """See `z3c.langauge.switch.interfaces.II18nLanguageSwitch`"""
        return self._language

    def setLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.II18nLanguageSwitch`"""
        self._language = language


class I18nAdapter(object):
    """Mixing class for i18n adapters which must provide the adapted object 
       under the attribute 'self.i18n'.
    """
    zope.interface.implements(II18n)

    # z3c.langauge.switch.IReadI18n
    def getAvailableLanguages(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        return self.i18n.getAvailableLanguages()

    def getDefaultLanguage(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        return self.i18n.getDefaultLanguage()

    def getPreferedLanguage(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        return self.i18n.getPreferedLanguage()

    def getAttribute(self, name, language=None):
        return self.i18n.getAttribute(name, language)
        
    def queryAttribute(self, name, language=None, default=None):
        return self.i18n.queryAttribute(name, language, default)

    # z3c.langauge.switch.IWriteI18n interface
    def setDefaultLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        return self.i18n.setDefaultLanguage(language)

    def addLanguage(self, language, *args, **kw):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        return self.i18n.addLanguage(language, *args, **kw)

    def removeLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        self.i18n.removeLanguage(language)

    def setAttributes(self, language, **kws):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        self.i18n.setAttributes(language, **kws)
