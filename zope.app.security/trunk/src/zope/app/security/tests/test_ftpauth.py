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
"""FTP Authentication Test

$Id$
"""
import unittest
from zope.testing import doctest

def test_bbb_imports():
    """
    Let's check if original imports still work:

      >>> import zope.app.security.ftpauth as old
      >>> import zope.publisher.ftp as new

      >>> old.FTPAuth is new.FTPAuth
      True

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
