##############################################################################
#
# Copyright (c) 2009 Paul Carduner and Stephan Richter.
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

from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer
from z3c.formui.interfaces import IDivFormLayer
from zope.container.interfaces import IContainer
from zope.container.constraints import contains
from zope.schema import ASCIILine

from z3c.feature.core.interfaces import IFeature

class IBuilderBrowserLayer(IBrowserRequest):
    """Builder Browser Layer"""

class IBuilderBrowserSkin(IFormLayer, IDivFormLayer, IBuilderBrowserLayer, IPageletBrowserLayer):
    """Skin for builder browser."""

class IBuildSession(IContainer):
    contains(IFeature)

    name = ASCIILine(title=u"Project Name")


    def addFeature(entryPoint):
        """Construct a feature from a web feature entry point."""


    def toXML(self, asString, prettyPrint):
        """Return xml project representation."""
