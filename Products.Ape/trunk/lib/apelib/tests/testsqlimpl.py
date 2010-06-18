##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Interface implementation tests

$Id$
"""

import unittest

from testimpl import InterfaceImplChecker


class ApelibSQLImplTests(InterfaceImplChecker, unittest.TestCase):

    def test_sql_implementations(self):
        import apelib.sql
        import apelib.sql.oidgen
        self._test_all_in_package(apelib.sql)

if __name__ == '__main__':
    unittest.main()

