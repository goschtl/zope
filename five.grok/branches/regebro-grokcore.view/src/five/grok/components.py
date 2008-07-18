import sys, os
import warnings

import martian
from zope import interface
from zope import component
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.pagetemplate.engine import TrustedAppPT
from zope.pagetemplate import pagetemplate, pagetemplatefile

from grokcore.component.interfaces import IContext
from grokcore.view.components import ViewMixin

from zope.publisher.publish import mapply

import Acquisition
from OFS.SimpleItem import SimpleItem

from zope.app.container.contained import Contained
import persistent

from zope.publisher.browser import BrowserPage

class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, IContext)

class View(ViewMixin, BrowserPage, Acquisition.Implicit):
    pass

class IGrokLayer(interface.Interface):
    pass

class Skin(object):
    pass