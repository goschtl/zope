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

$Id: I18nFile.py,v 1.1 2002/06/24 15:44:25 mgedmin Exp $
"""

import Persistence
from IFile import IFile
from Zope.I18n.II18nAware import II18nAware
from File import File


class II18nFile(IFile, II18nAware):
    """I18n aware file interface."""

    def removeLanguage(language):
        '''Remove translated content for a given language.'''


class I18nFile(Persistence.Persistent):
    """I18n aware file object."""

    __implements__ = II18nFile

    def __init__(self, data='', contentType=None, defaultLanguage='en'):
        """ """

        self._data = {}
        self.setData(data, language=defaultLanguage)
        self.setDefaultLanguage(defaultLanguage)

        if contentType is None:
            self._contentType = ''
        else:
            self._contentType = contentType


    def __len__(self):
        return self.getSize()


    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.IFile.IFile

    def setContentType(self, contentType):
        '''See interface IFile'''
        self._contentType = contentType


    def getContentType(self):
        '''See interface IFile'''
        return self._contentType


    def edit(self, data, contentType=None, language=None):
        '''See interface IFile'''

        # XXX This seems broken to me, as setData can override the
        # content type explicitly passed in.

        if contentType is not None:
            self._contentType = contentType
        self.setData(data, language)


    def getData(self, language=None):
        '''See interface IFile'''
        file = self._data.get(language)
        if not file:
            file = self._data[self.defaultLanguage]
        return file.getData()


    def setData(self, data, language=None):
        '''See interface IFile'''

        if language is None:
            language = self.defaultLanguage
        file = self._data.get(language)
        if file:
            file.setData(data)
        else:
            self._data[language] = File(data)
            self._p_changed = 1


    def getSize(self, language=None):
        '''See interface IFile'''
        file = self._data.get(language)
        if not file:
            file = self._data[self.defaultLanguage]
        return file.getSize()

    #
    ############################################################

    ############################################################
    # Implementation methods for interface
    # II18nAware.py

    def getDefaultLanguage(self):
        'See Zope.I18n.II18nAware.II18nAware'
        return self.defaultLanguage

    def setDefaultLanguage(self, language):
        'See Zope.I18n.II18nAware.II18nAware'
        if not self._data.has_key(language):
            raise ValueError, \
                  'cannot set nonexistent language (%s) as default' % language
        self.defaultLanguage = language

    def getAvailableLanguages(self):
        'See Zope.I18n.II18nAware.II18nAware'
        return self._data.keys()

    #
    ############################################################


    ############################################################
    # Implementation methods for interface
    # II18nFile.py
    def removeLanguage(self, language):
        '''See interface II18nFile'''

        if language == self.defaultLanguage:
            raise ValueError, 'cannot remove default language (%s)' % language
        if self._data.has_key(language):
            del self._data[language]
            self._p_changed = 1


