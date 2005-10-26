##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test local sites

$Id$
"""
import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_beforeAndAfterTraversal():
    """Test component lookup before and after traversal

    Set up:

      >>> import Products.Five
      >>> from Products.Five import zcml
      >>> zcml.load_config("configure.zcml", Products.Five)
      >>> zcml_text = '''\\
      ... <five:localsite
      ...   xmlns:five="http://namespaces.zope.org/five"
      ...   class="Products.Five.testing.localsite.DummySite" />'''
      >>> zcml.load_string(zcml_text)

    Before we set up the traversal hook that sends the traversal event
    for us, a look up of the local site will yield nothing:

      >>> from zope.app.component.hooks import getSite
      >>> response = http(r'''
      ... GET /test_folder_1_ HTTP/1.1
      ... ''')
      >>> getSite() is None
      True

      >>> from zope.component import getServices, getGlobalServices
      >>> getServices() is getGlobalServices()
      True

    Now we add a site with a stub site manager...

      >>> from Products.Five.site.tests.test_sitemanager import Folder, ServiceServiceStub
      >>> f1 = Folder()
      >>> f1.id = 'f1'
      >>> nothing = self.folder._setObject('f1', f1)
      >>> f1 = self.folder._getOb('f1')
      >>> sm = ServiceServiceStub()
      >>> f1.setSiteManager(sm)

    ... and enable the site traversal hook:

      >>> from Products.Five.site.localsite import enableLocalSiteHook
      >>> enableLocalSiteHook(f1)

    Now getServices() will return the stub site manager:

      >>> path = '/'.join(f1.getPhysicalPath())
      >>> response = http(r'''
      ... GET /test_folder_1_/f1 HTTP/1.1
      ... ''')
      >>> getServices() is sm
      True


    Finally, clean up the traversal hook as well as global services:

      >>> from zope.app.component.localservice import clearSite
      >>> clearSite()

      >>> from zope.app.tests.placelesssetup import tearDown
      >>> tearDown()
    """

def test_suite():
    from Testing.ZopeTestCase import FunctionalDocTestSuite
    return FunctionalDocTestSuite()

if __name__ == '__main__':
    framework()
