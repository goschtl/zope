from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable

from grokcore.component.interfaces import IContext

import Acquisition
from OFS.SimpleItem import SimpleItem

from grokcore.view import GrokView

class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, IContext)

class View(GrokView, Acquisition.Implicit):
    pass