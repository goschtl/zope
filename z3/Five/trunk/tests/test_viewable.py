##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Unit tests for the viewable module.

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


def test_defaultView():
    """
    Take a class Foo and an interface I1::

      >>> class Foo:
      ...     pass

      >>> from zope.interface import Interface
      >>> class I1(Interface):
      ...     pass

    Set up a default view for I1::

      >>> from zope.app import zapi
      >>> pres = zapi.getGlobalService('Presentation')
      >>> from zope.publisher.interfaces.browser import IBrowserRequest
      >>> pres.setDefaultViewName(I1, IBrowserRequest, 'foo.html')

    and a BrowserDefault for an instance of Foo::

      >>> foo = Foo()
      >>> from Products.Five.viewable import BrowserDefault
      >>> bd = BrowserDefault(foo)

    You'll see that no default view is returned::

      >>> request = self.app.REQUEST
      >>> obj, path = bd.defaultView(request)
      >>> obj is foo
      True
      >>> path is None
      True

    unless you mark the object with I1::

      >>> from zope.interface import directlyProvides
      >>> directlyProvides(foo, I1)
      >>> obj, path = bd.defaultView(request)
      >>> obj is foo
      True
      >>> path
      ['foo.html']

    """


def test_suite():
    from Testing.ZopeTestCase import installProduct, ZopeDocTestSuite
    installProduct('Five')
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
