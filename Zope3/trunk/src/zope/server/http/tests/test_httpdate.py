##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

$Id: test_httpdate.py,v 1.1 2003/01/09 12:45:33 anthony Exp $
"""

import unittest
from zope.server.http.http_date import build_http_date, parse_http_date

class Tests(unittest.TestCase):

    # test roundtrip conversion.
    def testDateRoundTrip(self):
	from time import time
	t = int(time())
	self.assertEquals(t, parse_http_date(build_http_date(t)))


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Tests)

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
