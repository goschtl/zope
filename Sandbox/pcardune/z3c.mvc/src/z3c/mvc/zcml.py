##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.component.zcml
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import z3c.template.interfaces

from z3c.mvc.template import TemplateFactory
from z3c.mvc.interfaces import IModelTemplate


def templateDirective(
    _context, template, name=u'',
    for_=zope.interface.Interface, layer=IDefaultBrowserLayer,
    provides=IModelTemplate,
    contentType='text/html', macro=None):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = TemplateFactory(template, contentType, macro)
    zope.interface.directlyProvides(factory, provides)

    # register the template
    if name:
        zope.component.zcml.adapter(_context, (factory,), provides,
                                    (for_, layer), name=name)
    else:
        zope.component.zcml.adapter(_context, (factory,), provides,
                                    (for_, layer))
