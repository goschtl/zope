##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Directives Tests

$Id: test_directives.py,v 1.2 2004/03/22 00:52:28 srichter Exp $
"""
import unittest
from zope.interface import Interface
from zope.testing.doctestunit import DocTestSuite

from zope.app.tests.placelesssetup import setUp, tearDown

class FauxContext:
    def __init__(self):
        self.actions = []

    def action(self, **kw):
        self.actions.append(kw)

class IDummyUtility(Interface):
    """Represents a dummy utility."""

def test_toolDirective():
    r"""
    >>> from zope.app.site.browser import metaconfigure
    >>> context = FauxContext()
    >>> metaconfigure.tool(context, IDummyUtility, folder="dummy",
    ...                    title="dummy", description="the description")

    >>> iface = context.actions[0]
    >>> iface['discriminator']
    >>> iface['callable'].__module__
    'zope.app.component.interface'
    >>> iface['args'][1].getName()
    'IDummyUtility'
    >>> iface['args'][2].getName()
    'IToolType'

    >>> view = context.actions[1]
    >>> print '\n'.join([str(n) for n in view['discriminator']])
    view
    (<InterfaceClass zope.app.site.interfaces.ISiteManager>,)
    manageIDummyUtilityTool.html
    <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>
    default
    <InterfaceClass zope.interface.Interface>
    >>> view['callable'].__module__
    'zope.app.component.metaconfigure'
    >>> view['args'][5]
    'manageIDummyUtilityTool.html'
    """


def _test_servicetoolDirective():
    r"""
    >>> from zope.app.site.browser import metaconfigure
    >>> context = FauxContext()
    >>> metaconfigure.servicetool(context, folder="dummy",
    ...                    title="dummy", description="the description")

    >>> iface = context.actions[0]
    >>> iface['discriminator']
    >>> iface['callable'].__module__
    'zope.app.component.interface'
    >>> iface['args'][1].getName()
    'ILocalService'
    >>> iface['args'][2].getName()
    'IToolType'

    >>> view = context.actions[1]
    >>> print '\n'.join([str(n) for n in view['discriminator']])
    view
    (<InterfaceClass zope.app.site.interfaces.ISiteManager>,)
    manageILocalServiceTool.html
    <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>
    default
    <InterfaceClass zope.interface.Interface>
    >>> view['callable'].__module__
    'zope.app.component.metaconfigure'
    >>> view['args'][5]
    'manageILocalServiceTool.html'
    """

def test_suite():
    return unittest.TestSuite((
        DocTestSuite(setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__': unittest.main()
