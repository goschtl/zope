from zope import interface
from zope import component

from zope.app.publisher.browser.directoryresource import Directory
from zope.security.checker import CheckerPublic

import lxml.html
import interfaces
import utils

class Layout(object):
    interface.implements(interfaces.ILayout)

    def __init__(self, name, template, resource_path, regions=None):
        self.name = name
        self.template = template
        self.regions = regions or set()
        self.resource_path = resource_path
        
    def parse(self):
        tree = lxml.html.parse(self.template)
        utils.rebase(tree, self.resource_path)
        return tree
    
class Region(object):
    interface.implements(interfaces.IRegion)

    def __init__(self, name, xpath, title=u"", mode="replace", provider=None):
        self.name = name
        self.xpath = xpath
        self.title =  title
        self.mode = mode
        self.provider = provider
        
    def __repr__(self):
        return "<%s %s %s (%s) %s>" % (
            self.__class__.__name__,
            repr(self.name),
            self.xpath,
            self.mode,
            repr(self.provider))
