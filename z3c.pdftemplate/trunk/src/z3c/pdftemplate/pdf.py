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
"""PDF generation base classes

$Id$
"""
__docformat__ = "reStructuredText"

import xml.dom.minidom
from StringIO import StringIO
from zope.publisher.browser import BrowserView
from z3c.pdftemplate.pml2pdf.Parser import TemplateParser

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
        # create the PDFTemplate from xml
        template_xml = self.template(self).encode('utf-8')
        template_dom = xml.dom.minidom.parseString(template_xml)
        template = TemplateParser(template_dom, 'utf-8', ResourceHandler())()
        # Boilerplate from PML :(
        template.title = ''
        template.author = ''
        template.subject = ''
        return template


class PDFView(PDFTemplateGenerator, BrowserView):
    """Base-class for objects rendering PDFs using a template."""
    pass
