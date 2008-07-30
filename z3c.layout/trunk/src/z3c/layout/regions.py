from zope import interface

import interfaces

class Region(object):
    interface.implements(interfaces.IRegion)

    def __init__(self, name, xpath, title=None):
        self.name = name
        self.xpath = xpath
        self.title =  title

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, repr(self.name))
