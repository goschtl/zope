# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################
"""RML-to-PDF View

$Id$
"""
__docformat__ = "reStructuredText"

from StringIO import StringIO
from zope.publisher.browser import BrowserPage
from z3c.pdftemplate import trml2pdf


class ResourceHandler:
    """Wrapper to allow loading from external resources.

    The implementation forbids local file access for security reasons.
    """

    def get(self, url, data=None):
        url = str(url)
        if url.startswith('file:'):
            raise urllib2.URLError, \
                  'The file: protocol is disabled for security'
        fd = self.opener.open(url, data)
        return StringIO(fd.read())

class PDFTemplateGenerator(object):

    template = None

    def getPDFTemplate(self):
        return self.template(self).encode('iso-8859-1')

class RML2PDFView(PDFTemplateGenerator, BrowserPage):

    document = None

    def __call__(self):

        rmldocument = self.document(self).encode('iso-8859-1')

        self.request.response.setHeader('content-type', 'application/pdf')

        return trml2pdf.parseString(rmldocument)
