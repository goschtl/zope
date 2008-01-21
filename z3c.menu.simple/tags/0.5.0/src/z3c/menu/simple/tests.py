##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
import zope.security
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup, ztapi
from zope.app.testing import functional


class TestParticipation(object):
    principal = 'foobar'
    interaction = None


def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root


    # resource namespace setup
    from zope.traversing.interfaces import ITraversable
    from zope.traversing.namespace import resource
    ztapi.provideAdapter(None, ITraversable, resource, name="resource")
    ztapi.provideView(None, None, ITraversable, "resource", resource)

    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

    zope.security.management.getInteraction().add(TestParticipation())


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
