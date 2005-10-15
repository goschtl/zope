##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Portlet implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import sys
import zope.interface
from zope.viewlet.viewlet import SimpleAttributeViewlet
from zope.viewlet.viewlet import ViewletBase
from zope.portlet import interfaces

from zope.app.pagetemplate.simpleviewclass import simple



class DefaultPortletManager(object):
    """Default portlet manager."""

    zope.interface.implements(interfaces.IPortletManager)


class SimplePortlet(ViewletBase):
    """Portlet adapter class used in meta directive as a mixin class."""

    zope.interface.implements(interfaces.IPortlet)

    def __init__(self, context, request, view):
        super(SimplePortlet, self).__init__(context, request, view)


class SimpleAttributePortlet(SimpleAttributeViewlet):
    """Simple attribute based portlet."""


def SimplePortletClass(template, offering=None, bases=(), name=u'', weight=0):
    # Get the current frame
    if offering is None:
        offering = sys._getframe(1).f_globals

    # Create the base class hierarchy
    bases += (SimplePortlet, simple)

    # Generate a derived view class.
    class_ = type("SimplePortletClass from %s" % template, bases,
                  {'index' : ViewletPageTemplateFile(template, offering),
                   '_weight' : weight,
                   '__name__' : name})

    return class_
