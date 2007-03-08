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
"""ReST-to-PDF Resources

$Id$
"""
__docformat__ = "reStructuredText"

import xml.dom.minidom
from docutils.core import publish_string
from StringIO import StringIO

from zope.interface import implements
from zope.app.publisher.browser.resource import Resource
from zope.publisher.interfaces.browser import IBrowserPublisher

import z3c.pdftemplate.rlpdf.rlpdf
from z3c.pdftemplate.pml2pdf.Parser import DocumentParser
from z3c.pdftemplate.pdf import PDFTemplateGenerator


class PDFWriter(z3c.pdftemplate.rlpdf.rlpdf.Writer):

    def __init__(self, template):
        z3c.pdftemplate.rlpdf.rlpdf.Writer.__init__(self)
        self.doc = template
        self.doc.subject = ''

    def translate(self):
        visitor = self.translator_class(self.document)
        visitor.styleSheet = self.doc.getStyleSheet()
        self.document.walkabout(visitor)
        self.story = visitor.as_what()
        self.output = self.record()

    def record(self):
        out = StringIO()
        self.doc.filename = out
        self.doc.build(self.story)
        return out.getvalue()

class ReSTPDFResource(PDFTemplateGenerator, Resource):

    implements(IBrowserPublisher)

    def __init__(self, path, template, request):
        self.path = path
        self.template = template
        self.request = request
        # Needed for the page template view class
        self.context = template

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return self, ()

    def __call__(self):
        template = self.getPDFTemplate()
        pdf = publish_string(open(self.path, 'r').read(),
                             writer=PDFWriter(template))

        # Set the content type to application/pdf
        self.request.response.setHeader('content-type', 'application/pdf')
        
        return pdf


class ReSTPDFResourceFactory(object):
    """A factory that generates PDF generating resource."""

    def __init__(self, path, template):
        self.__path = path
        self.__template = template

    def __call__(self, request):
        return ReSTPDFResource(self.__path, self.__template, request)
