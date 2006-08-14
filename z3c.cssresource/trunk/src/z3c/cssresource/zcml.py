##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Meta Configure

$Id$
"""
import zope.schema
import zope.configuration.fields
from zope.component.zcml import handler
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.publisher.browser import metadirectives

from z3c.cssresource import cssresource


class ICSSResourceDirective(metadirectives.IBasicResourceInformation):
    """Defines a browser CSS resource"""

    name = zope.schema.TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
        )

    file = zope.configuration.fields.Path(
        title=u"File",
        description=u"The file containing the resource data.",
        required=True
        )


def cssresource(_context, name, file, layer=IDefaultBrowserLayer,
                permission='zope.Public'):

    factory = cssresource.CSSFileResourceFactory(file, checker, name)

    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter',
                factory, (layer,), Interface, name, _context.info),
        )
