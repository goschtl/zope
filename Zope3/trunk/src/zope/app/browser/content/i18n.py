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

$Id: i18n.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n.negotiator import negotiator
from zope.publisher.browser import BrowserView


class I18nFileView(BrowserView):

    def __call__(self):
        """Call the File"""
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


class I18nFileEdit(BrowserView):

    __implements__ = BrowserView.__implements__

    name = 'editForm'
    title = 'Edit Form'
    description = ('This edit form allows you to make changes to the ' +
                   'properties of this file.')

    template = ViewPageTemplateFile('i18n_edit.pt')

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
                      "/editForm.html?language=%s" % language)  # XXX url_quote
