import os

from zope import interface
from zope import component

from z3c.layout.interfaces import ILayout
from z3c.layout.interfaces import IRegion


class Layout(object):
    interface.implements(ILayout)

    def __init__(self, name, resource_directory, template, thumbnail):
        self.name = name
        self.resource_directory = resource_directory
        self.template = template
        self.thumbnail = thumbnail
        self.regions = []
