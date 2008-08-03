import martian

from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable

import grokcore.view
from grokcore.component.interfaces import IContext

import Acquisition
from OFS.SimpleItem import SimpleItem

class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, IContext)

class View(grokcore.view.View, Acquisition.Explicit):
    pass
