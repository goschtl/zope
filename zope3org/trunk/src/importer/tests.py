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
"""

$Id:$
"""

import unittest

from os.path import dirname, join

from zope.testing import doctest

from zope.app import zapi
from zope.app.testing import ztapi

from importer.testing import placelesssetup

testURL = "file:" + join(dirname(__file__), "testsite", "FrontPage")

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', 
                                setUp=placelesssetup.setUp, 
                                tearDown=placelesssetup.tearDown,
                                globs={'zapi': zapi, 
                                        'ztapi': ztapi, 
                                        'download_url': testURL},
                                optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS
                             ),
        doctest.DocTestSuite('importer.zopeorgwikiimporter',
                              optionflags=doctest.NORMALIZE_WHITESPACE+
                                          doctest.ELLIPSIS
                            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
