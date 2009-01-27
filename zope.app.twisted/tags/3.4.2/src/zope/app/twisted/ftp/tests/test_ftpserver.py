##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test the FTP server.
"""

from unittest import TestSuite, main

from zope.testing import doctest

def test_suite():
    return TestSuite((
        doctest.DocTestSuite('zope.app.twisted.ftp.server'),
        doctest.DocTestSuite('zope.app.twisted.ftp.utils'),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
