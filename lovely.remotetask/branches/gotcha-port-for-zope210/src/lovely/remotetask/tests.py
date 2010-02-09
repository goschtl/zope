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

"""
__docformat__ = "reStructuredText"

from lovely.remotetask import service
from zope.app.testing.setup import (placefulSetUp, placefulTearDown)
from zope.testing.doctest import INTERPRET_FOOTNOTES
from zope.testing.doctestunit import DocFileSuite
from zope.testing.loggingsupport import InstalledHandler
import doctest
import random
import unittest


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root

    log_info = InstalledHandler('lovely.remotetask')
    test.globs['log_info'] = log_info
    test.origArgs = service.TaskService.processorArguments
    service.TaskService.processorArguments = {'waitTime': 0.0}
    # Make tests predictable
    random.seed(27)


def tearDown(test):
    random.seed()
    placefulTearDown()
    log_info = test.globs['log_info']
    log_info.clear()
    log_info.uninstall()
    service.TaskService.processorArguments = test.origArgs


class TestIdGenerator(unittest.TestCase):

    def setUp(self):
        random.seed(27)
        self.service = service.TaskService()

    def tearDown(self):
        random.seed()

    def test_sequence(self):
        initial_id = self.service._generateId()
        self.assertEquals(initial_id + 1, self.service._generateId())
        self.assertEquals(initial_id + 2, self.service._generateId())
        self.assertEquals(initial_id + 3, self.service._generateId())

    def test_in_use_randomises(self):
        initial_id = self.service._generateId()
        self.service.jobs[initial_id] = object()
        second_id = self.service._generateId()
        self.assertNotEquals(second_id, initial_id)
        self.assertEquals(second_id + 1, self.service._generateId())
        self.service.jobs[second_id + 2] = object()
        next_id = self.service._generateId()
        self.assertNotEquals(next_id, second_id)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestIdGenerator),
        DocFileSuite('README.txt',
                     'startlater.txt',
                     'processor.txt',
                     'TESTING.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE
                     | doctest.ELLIPSIS
                     | INTERPRET_FOOTNOTES),
        ))
