##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Remote Task test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import logging
import unittest
from zope.app.testing import placelesssetup
from zope.app.testing.setup import (placefulSetUp,
                                    placefulTearDown)
from zope.testing.doctestunit import DocFileSuite
from zope.testing.doctest import INTERPRET_FOOTNOTES
from zope.testing.loggingsupport import InstalledHandler

from lovely.remotetask import service

def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root

    log_info = InstalledHandler('lovely.remotetask')
    test.globs['log_info'] = log_info
    test.origArgs = service.TaskService.processorArguments
    service.TaskService.processorArguments = {'waitTime': 0.0}

def tearDown(test):
    placefulTearDown()
    log_info = test.globs['log_info']
    log_info.clear()
    log_info.uninstall()
    service.TaskService.processorArguments = test.origArgs

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     |doctest.ELLIPSIS
                     |INTERPRET_FOOTNOTES
                     ),
        DocFileSuite('startlater.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     |doctest.ELLIPSIS
                     ),
        DocFileSuite('processor.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     |doctest.ELLIPSIS
                     ),
        DocFileSuite('TESTING.txt',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
