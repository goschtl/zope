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

"""Test that the package's configure.zcml can be loaded."""

import unittest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration.tests.test_xml import TempFile
from zope.configuration.xmlconfig import XMLConfig


class TestBrowserFormZCML(PlacelessSetup, unittest.TestCase):

    def test_load_zcml(self):
        text = """\
        <zopeConfigure xmlns='http://namespaces.zope.org/zope'>
          <include package='zope.configuration' file='metameta.zcml' />
          <include package='zope.app.component' file='meta.zcml' />
          <include package='zope.app.event' file='meta.zcml' />
          <include package='zope.app.publisher.browser' file='meta.zcml' />

          <include package='zope.app.browser.form' />
        </zopeConfigure>
        """
        f = TempFile()
        try:
            f.write(text)
            f.flush()
            x = XMLConfig(f.name)
            x()
        finally:
            f.close()


def test_suite():
    return unittest.makeSuite(TestBrowserFormZCML)

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
