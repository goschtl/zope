##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Simple content class(es) for browser tests

$Id$
"""
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from zope.interface import Interface, implements
from Products.Five.traversable import Traversable

class ISimpleContent(Interface):
    pass

class ICallableSimpleContent(ISimpleContent):
    pass

class IIndexSimpleContent(ISimpleContent):
    pass

class SimpleContent(Traversable, SimpleItem):
    implements(ISimpleContent)

    meta_type = 'Five SimpleContent'
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security.declarePublic('mymethod')
    def mymethod(self):
        return "Hello world"

    security.declarePublic('direct')
    def direct(self):
        """Should be able to traverse directly to this as there is no view.
        """
        return "Direct traversal worked"

InitializeClass(SimpleContent)

class CallableSimpleContent(SimpleItem):
    """A Viewable piece of content"""
    implements(ICallableSimpleContent)

    meta_type = "Five CallableSimpleContent"

    def __call__(self, *args, **kw):
        """ """
        return "Default __call__ called"

InitializeClass(CallableSimpleContent)

class IndexSimpleContent(SimpleItem):
    """A Viewable piece of content"""
    implements(IIndexSimpleContent)

    meta_type = 'Five IndexSimpleContent'

    def index_html(self, *args, **kw):
        """ """
        return "Default index_html called"

InitializeClass(IndexSimpleContent)

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add the simple content."""
    self._setObject(id, SimpleContent(id, title))

def manage_addCallableSimpleContent(self, id, title, REQUEST=None):
    """Add the viewable simple content."""
    self._setObject(id, CallableSimpleContent(id, title))

def manage_addIndexSimpleContent(self, id, title, REQUEST=None):
    """Add the viewable simple content."""
    self._setObject(id, IndexSimpleContent(id, title))
