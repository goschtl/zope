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
"""``pdf`` directive for generating PDFs from PML

$Id$
"""
__docformat__ = "reStructuredText"

from zope.interface import Interface
from zope.schema import TextLine
from zope.configuration.fields import Path
from zope.app.publisher.browser.metadirectives import IViewDirective
from zope.app.publisher.browser.metadirectives import IBasicResourceInformation


class IPDFBaseDirective(Interface):
    """Base directive for PDF-generating browser views.

    All PDF-generating components of this package require some information on
    how to layout the PDF page, such as the page layout and style sheet. All
    of this information is contained in a PML-based template.
    """
    template = Path(
        title=u"PML Template Page Template",
        description=u"""
        Refers to a file containing a page template that will generate the
        PML template/style file for PDF generation.""",
        required=False
        )

class IPDFDirective(IPDFBaseDirective, IViewDirective):
    """A simple view directive that generates PDFs.

    Most of the work is up to the view class you are providing, since you have
    to specify how the PDF is generated. The only help you are getting is that
    the PDF layout template is generated for you.
    """

class IPMLToPDFDirective(IPDFDirective):
    """A view directive that dynamically evaluates a PML document and converts
    it to PDF.

    This directive behaves very much like the ``page`` directive, except that
    it does not generate HTML, but PML that is rendered to PDF for output. PML
    is a simple XML-dialect that creates a storyboard for the reportlab PDF
    rendering engine.
    """

    document = Path(
        title=u"PML Document Page Template",
        description=u"""
        Refers to a file containing a page template that will generate the
        PML data file for PDF generation.""",
        required=True
        )

class IReSTToPDFDirective(IPDFBaseDirective, IBasicResourceInformation):
    """A resource directive that converts ReST documents to PDF.

    All you basically need to do is specify a the path to the ReST file. If
    you do not provide your own template file, a sensible default PDF template
    is provided.
    """

    name = TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
        )

    path = Path(
        title=u"Path of the ReST File",
        description=u"""Refers to the path of the ReST file.""",
        required=True
        )

class IRMLToPDFDirective(Interface, IViewDirective):
    """A view directive that dynamically evaluates a RML document and converts
    it to PDF.

    This directive behaves very much like the ``page`` directive, except that
    it does not generate HTML, but RML that is rendered to PDF for output. RML
    is a simple XML-dialect that creates a storyboard for the reportlab PDF
    rendering engine.
    """

    document = Path(
        title=u"RML Document Page Template",
        description=u"""
        Refers to a file containing a page template that will generate the
        RML data file for PDF generation.""",
        required=True
        )  