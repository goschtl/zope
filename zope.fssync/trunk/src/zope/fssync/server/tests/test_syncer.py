##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the general synchronizer.

$Id$
"""
import os
import shutil
import tempfile
import unittest

from zope.fssync.server import syncer, interfaces
from zope.interface import implements


class MyError(Exception):
    pass


class MySerializer(object):

    implements(interfaces.IObjectDirectory)

    def __init__(self, context):
        pass

    def extra(self):
        return None

    def typeIdentifier(self):
        return "good.type"

    def factory(self):
        return "good.factory"

    def contents(self):
        return {}


def raise_error(obj):
    raise MyError


class SyncerTestCase(unittest.TestCase):

    def setUp(self):
        self.location = tempfile.mktemp()
        os.mkdir(self.location)

    def tearDown(self):
        shutil.rmtree(self.location)

    def test_calling_getObjectId(self):
        s = syncer.Syncer(raise_error, MySerializer)
        self.assertRaises(MyError,
                          s.toFS, 42, "foo", self.location)

    def test_calling_getSerializer(self):
        s = syncer.Syncer(lambda obj: "/foo/bar", raise_error)
        self.assertRaises(MyError,
                          s.toFS, 42, "foo", self.location)

    def test_calling_both(self):
        s = syncer.Syncer(lambda obj: "/foo/bar", MySerializer)
        s.toFS(42, "foo", self.location)

    def test_calling_getAnnotations(self):
        s = syncer.Syncer(lambda obj: "/foo/bar", MySerializer,
                          raise_error)
        self.assertRaises(MyError,
                          s.toFS, 42, "foo", self.location)


def test_suite():
    return unittest.makeSuite(SyncerTestCase)
