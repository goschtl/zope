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
"""I18n versions of several content objects.

$Id: i18nfile.py,v 1.2 2004/02/24 16:50:08 philikon Exp $
"""
from zope.i18n.negotiator import negotiator

__metaclass__ = type

class I18nFileView:

    def __call__(self):
        """Call the File
        """
        request = self.request
        language = None
        if request is not None:
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, request)

            request.response.setHeader('Content-Type',
                                       self.context.getContentType())
            request.response.setHeader('Content-Length',
                                       self.context.getSize(language))

        return self.context.getData(language)


class I18nFileEdit:

    name = 'editForm'
    title = 'Edit Form'
    description = ('This edit form allows you to make changes to the ' +
                   'properties of this file.')

    def action(self, contentType, data, language, defaultLanguage,
               selectLanguage=None, removeLanguage=None,
               addLanguage=None, newLanguage=None):
        if selectLanguage:
            pass
        elif removeLanguage:
            self.context.removeLanguage(language)
            language = self.context.getDefaultLanguage()
        else:
            if addLanguage:
                language = newLanguage
            self.context.setDefaultLanguage(defaultLanguage)
            self.context.edit(data, contentType, language)
        return self.request.response.redirect(self.request.URL[-1] +
                      "/editForm.html?language=%s" %language)  # XXX url_quote
