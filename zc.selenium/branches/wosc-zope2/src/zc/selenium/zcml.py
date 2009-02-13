##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""A simple directive for selenium tests.

$Id$
"""
__docformat__ = "reStructuredText"
import os
import zope.interface
from zope.app.component.back35 import LayerField
from zope.component import zcml
from zope.app.publisher.browser import resourcemeta
from zope.configuration.fields import Path
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import CheckerPublic, NamesChecker
from zope.security.zcml import Permission
from zc.selenium import htmltest

class ISeleniumTest(zope.interface.Interface):
    """A directive to register an HTML selenium test with the selenium test
    runner."""

    file = Path(
        title=u"File",
        description=u"The file the HTML selenium test.",
        required=True
        )

    layer = LayerField(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False
        )

    permission = Permission(
        title=u"The permission needed to access the resource.",
        description=u"""
        If a permission isn't specified, the resource will always be
        accessible.""",
        required=False
        )

def seleniumTest(_context, file, layer=IBrowserRequest,
                 permission='zope.Public'):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(resourcemeta.allowed_names, permission)

    SeleniumTestFactory = htmltest.createSeleniumTest(str(file))
    SeleniumTestFactory.__Security_checker__ = checker
    name = os.path.split(file)[-1]

    zcml.adapter(_context,
                 factory=(SeleniumTestFactory,), for_=(layer,), name=name)
