##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Test harness for gocept.registration."""

import os.path
import re
import unittest
import zope.testing.renormalizing
import zope.sendmail.interfaces

from zope.app.testing import placelesssetup, functional
from zope.testing import doctest


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[a-z0-9]{40}'), '<SHA-HASH>')])


class DummyMailer(object):
    """A dummy mailer."""

    zope.interface.implements(zope.sendmail.interfaces.IMailDelivery)

    def send(self, fromaddr, toaddr, msg):
        print "(%s -> %s)" % (fromaddr, toaddr)
        print msg


RegistrationLayer = functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'RegistrationLayer_FTest')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
        checker=checker, setUp=placelesssetup.setUp,
        tearDown=placelesssetup.tearDown))
    demo = functional.FunctionalDocFileSuite(
        os.path.join('demo', 'README.txt'),
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
        checker=checker)
    demo.layer = RegistrationLayer
    suite.addTest(demo)
    return suite
