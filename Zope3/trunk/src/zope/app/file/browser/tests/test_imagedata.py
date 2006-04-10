##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test Image Data handling

$Id$
"""
import unittest

from zope.app.file.image import Image
from zope.app.file.browser.image import ImageData

class FakeRequest(object):
    pass

class Test(unittest.TestCase):

    def testData(self):
        """ """
        image = Image('Data')
        id = ImageData()
        id.context = image
        id.request = None
        self.assertEqual(id(), 'Data')

    def testTag(self):
        """ """

        # faking absolute_url getter .
        def absolute_url(context, request):
            return '/img'

        image = Image()
        fe = ImageData()
        fe.context = image
        fe.request = FakeRequest()

        from zope.app import zapi
        old_absoluteURL = zapi.absoluteURL
        try:
            zapi.absoluteURL = absolute_url
            self.assertEqual(fe.tag(),
                '<img src="/img" alt="" height="-1" width="-1" border="0" />')
            self.assertEqual(fe.tag(alt="Test Image"),
                '<img src="/img" alt="Test Image" '
                'height="-1" width="-1" border="0" />')
            self.assertEqual(fe.tag(height=100, width=100),
                ('<img src="/img" alt="" height="100" '
                 'width="100" border="0" />'))
            self.assertEqual(fe.tag(border=1),
                '<img src="/img" alt="" height="-1" width="-1" border="1" />')
            self.assertEqual(fe.tag(css_class="Image"),
                '<img src="/img" alt="" '
                'height="-1" width="-1" border="0" class="Image" />')
            self.assertEqual(fe.tag(height=100, width="100",
                            border=1, css_class="Image"),
                '<img src="/img" alt="" '
                'height="100" width="100" class="Image" border="1" />')
        finally:
            zapi.absoluteURL = old_absoluteURL

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.main()
