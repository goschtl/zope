##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Test Five-traversable classes

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


class SimpleClass(object):
    """Class with no __bobo_traverse__."""


def test_traversable():
    """
    Test the behaviour of Five-traversable classes.

      >>> import Products.Five
      >>> from Products.Five import zcml
      >>> zcml.load_config("configure.zcml", Products.Five)

    ``SimpleContent`` is a traversable class by default.  Its fallback
    traverser should raise NotFound when traversal fails.  (Note: If
    we return None in __fallback_traverse__, this test passes but for
    the wrong reason: None doesn't have a docstring so BaseRequest
    raises NotFoundError.)

      >>> from Products.Five.tests.testing.simplecontent import manage_addSimpleContent
      >>> manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
      >>> print http(r'''
      ... GET /test_folder_1_/testoid/doesntexist HTTP/1.1
      ... ''')
      HTTP/1.1 404 Not Found
      ...

    Now let's take class which already has a __bobo_traverse__ method.
    Five should correctly use that as a fallback.

      >>> configure_zcml = '''
      ... <configure xmlns="http://namespaces.zope.org/zope"
      ...            xmlns:meta="http://namespaces.zope.org/meta"
      ...            xmlns:browser="http://namespaces.zope.org/browser"
      ...            xmlns:five="http://namespaces.zope.org/five">
      ... 
      ... <!-- make the zope2.Public permission work -->
      ... <meta:redefinePermission from="zope2.Public" to="zope.Public" />
      ... 
      ... <five:traversable
      ...     class="Products.Five.tests.testing.fancycontent.FancyContent"
      ...     />
      ... <five:traversable
      ...     class="Products.Five.browser.tests.test_traversable.SimpleClass"
      ...     />
      ... <five:traversable
      ...     class="Products.Five.tests.testing.FiveTraversableFolder"
      ...     />
      ... 
      ... <browser:page
      ...     for="Products.Five.tests.testing.fancycontent.IFancyContent"
      ...     class="Products.Five.browser.tests.pages.FancyView"
      ...     attribute="view"
      ...     name="fancy"
      ...     permission="zope2.Public"
      ...     />
      ... 
      ... </configure>'''
      >>> zcml.load_string(configure_zcml)

      >>> from Products.Five.tests.testing.fancycontent import manage_addFancyContent
      >>> info = manage_addFancyContent(self.folder, 'fancy', '')

    In the following test we let the original __bobo_traverse__ method
    kick in:

      >>> print http(r'''
      ... GET /test_folder_1_/fancy/something-else HTTP/1.1
      ... ''')
      HTTP/1.1 200 OK
      ...
      something-else

    Of course we also need to make sure that Zope 3 style view lookup
    actually works:

      >>> print http(r'''
      ... GET /test_folder_1_/fancy/fancy HTTP/1.1
      ... ''')
      HTTP/1.1 200 OK
      ...
      Fancy, fancy
      
    Five's traversable monkeypatches the __bobo_traverse__ method to do view
    lookup and then delegates back to the original __bobo_traverse__ or direct
    attribute/item lookup to do normal lookup.  In the Zope 2 ZPublisher, an 
    object with a __bobo_traverse__ will not do attribute lookup unless the
    __bobo_traverse__ method itself does it (i.e. the __bobo_traverse__ is the
    only element used for traversal lookup).  Let's demonstrate:
        
      >>> from Products.Five.tests.testing.fancycontent import manage_addNonTraversableFancyContent
      >>> info = manage_addNonTraversableFancyContent(self.folder, 'fancy_zope2', '')
      >>> self.folder.fancy_zope2.an_attribute = 'This is an attribute'
      >>> print http(r'''
      ... GET /test_folder_1_/fancy_zope2/an_attribute HTTP/1.1
      ... ''')
      HTTP/1.1 200 OK
      ...
      an_attribute
      
    Without a __bobo_traverse__ method this would have returned the attribute
    value 'This is an attribute'.  Let's make sure the same thing happens for
    an object that has been marked traversable by Five:

      >>> self.folder.fancy.an_attribute = 'This is an attribute'
      >>> print http(r'''
      ... GET /test_folder_1_/fancy/an_attribute HTTP/1.1
      ... ''')
      HTTP/1.1 200 OK
      ...
      an_attribute


    Clean up:

      >>> from zope.app.tests.placelesssetup import tearDown
      >>> tearDown()

    Verify that after cleanup, there's no cruft left from five:traversable::

      >>> from Products.Five.browser.tests.test_traversable import SimpleClass
      >>> hasattr(SimpleClass, '__bobo_traverse__')
      False
      >>> hasattr(SimpleClass, '__fallback_traverse__')
      False

      >>> from Products.Five.tests.testing.fancycontent import FancyContent
      >>> hasattr(FancyContent, '__bobo_traverse__')
      True
      >>> hasattr(FancyContent.__bobo_traverse__, '__five_method__')
      False
      >>> hasattr(FancyContent, '__fallback_traverse__')
      False
    """

def test_suite():
    from Testing.ZopeTestCase import FunctionalDocTestSuite
    return FunctionalDocTestSuite()

if __name__ == '__main__':
    framework()
