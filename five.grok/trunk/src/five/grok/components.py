from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable

from OFS.SimpleItem import SimpleItem
from Products.Five import BrowserView

from five.grok import interfaces

from zope.app.container.contained import Contained
import persistent

class Model(Contained, persistent.Persistent):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, interfaces.IContext)
    
    
class View(BrowserView):
    
    def __call__(self):
        return self.render()

