##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""I18n versions of several content objects.

$Id$
"""
__docformat__ = 'restructuredtext'

from urllib import quote
from zope.i18n.negotiator import negotiator
from zope.app.i18n import ZopeMessageIDFactory as _

class I18nFileView(object):

    def __call__(self):
        """Call the File
        """
        request = self.request
        language = None
        if request is not None:
            langs = self.context.getAvailableLanguages()
            language = negotiator.getLanguage(langs, request)

            request.response.setHeader('Content-Type',
                                       self.context.contentType)
            request.response.setHeader('Content-Length',
                                       self.context.getSize(language))

        return self.context.getData(language)


class I18nFileEdit(object):

    name = 'editForm'
    title = _('Edit Form')
    description = _('This edit form allows you to make changes to the ' +
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
            self.context.setData(data, language)
            self.context.contentType = contentType
        return self.request.response.redirect(self.request.URL[-1] +
                      "/editForm.html?language=%s" % quote(language, ''))
