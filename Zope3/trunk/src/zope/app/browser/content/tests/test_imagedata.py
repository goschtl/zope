##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: test_imagedata.py,v 1.2 2002/12/25 14:12:31 jim Exp $
"""

import unittest

from zope.app.browser.content.image import ImageData
from zope.app.content.image import Image


class Test( unittest.TestCase ):

    def testData(self):
        """ """
        image = Image('Data')

        id = ImageData(image, None)

        self.assertEqual(id(), 'Data')


    def testTag(self):
        """ """

        # We need that, sinc eabsolute_url is not implemented yet.
        def absolute_url():
            return '/img'

        image = Image()
        fe = ImageData(image, None)
        fe.absolute_url = absolute_url

        self.assertEqual(fe.tag(),
            '<img src="/img" alt="" height="-1" width="-1" border="0" />')
        self.assertEqual(fe.tag(alt="Test Image"),
            '<img src="/img" alt="Test Image" '
            'height="-1" width="-1" border="0" />')
        self.assertEqual(fe.tag(height=100, width=100),
            '<img src="/img" alt="" height="100" width="100" border="0" />')
        self.assertEqual(fe.tag(border=1),
            '<img src="/img" alt="" height="-1" width="-1" border="1" />')
        self.assertEqual(fe.tag(css_class="Image"),
            '<img src="/img" alt="" '
            'height="-1" width="-1" border="0" class="Image" />')
        self.assertEqual(fe.tag(height=100, width="100",
                         border=1, css_class="Image"),
            '<img src="/img" alt="" '
            'height="100" width="100" class="Image" border="1" />')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.main()
