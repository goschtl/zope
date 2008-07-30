# -*- coding: utf-8 -*-
#
# File: metadirective.py
#

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: $"
__version__   = '$Revision: $'[11:-2]

from zope import component
from zope import interface
from zope import schema

from zope.app.publisher.browser.resourcemeta import resourceDirectory
from zope.configuration import fields
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.layout.regions import Region
from z3c.layout.layout import Layout
from z3c.layout.interfaces import ILayout

class ILayoutDirective(interface.Interface):
    """Layout."""

    name = schema.TextLine(
        title=u"Title")
    
    template = fields.Path(
        title=u"Template")
    
    thumbnail = fields.Path(
        title=u"Thumbnail")
    
    resource_directory = schema.TextLine(
        title=u"Resource directory")

class IRegionDirective(interface.Interface):
    """Layout region."""

    name = schema.TextLine(
        title=u"title")
    
    xpath = schema.TextLine(
        title=u"xpath")
    
    title = schema.TextLine(
        title=u"title")

class LayoutDirective(object):
    """
    Call order will be __init__, region, __call__
    """

    def __init__(self, _context, name, template, thumbnail, resource_directory):
        self._context = _context
        self.name = name
        self.resource_directory = resource_directory
        self.template = template
        self.thumbnail = thumbnail
        self.regions = []

    def region(self, _context, name, xpath, title):
        self.regions.append(Region(name=name, xpath=xpath, title=title))

    def __call__(self):
        layout = Layout(
            name = self.name,
            resource_directory = self.resource_directory,
            template = self.template,
            thumbnail = self.thumbnail)

        layout.regions = self.regions

        component.provideUtility(layout, ILayout, name=self.name)

# vim: set ft=python ts=4 sw=4 expandtab :
