##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
Internationalized file resource.

$Id: I18nFileResource.py,v 1.1 2002/06/25 14:30:08 mgedmin Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from Zope.Publisher.Browser.IBrowserResource import IBrowserResource
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher

from Zope.App.Publisher.FileResource import File, Image

from FileResource import FileResource

from Zope.I18n.Negotiator import negotiator
from Zope.I18n.II18nAware import II18nAware


class I18nFileResource(FileResource):

    __implements__ = IBrowserResource, IBrowserPublisher, II18nAware

    def __init__(self, data, request, defaultLanguage='en'):
        """Creates an internationalized file resource.  data should be
        a mapping from languages to File or Image objects.
        """
        self._data = data
        self.request = request
        self.defaultLanguage = defaultLanguage


    def chooseContext(self):
        """Choose the appropriate context according to language"""
        langs = self.getAvailableLanguages()
        language = negotiator.getLanguage(langs, self.request)
        try:
            return self._data[language]
        except KeyError:
            return self._data[self.defaultLanguage]


    # for unit tests
    def _testData(self, language):
        file = self._data[language]
        f=open(file.path,'rb')
        data=f.read()
        f.close()
        return data


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


class I18nFileResourceFactory:

    def __init__(self, data, defaultLanguage):
        self.__data = data
        self.__defaultLanguage = defaultLanguage

    def __call__(self, request):
        return I18nFileResource(self.__data, request, self.__defaultLanguage)

