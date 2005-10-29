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
"""Table doc tests

"""
__docformat__ = 'restructuredtext'

import unittest
import zope.interface
import zope.security
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup
from zope.configuration import xmlconfig



class TestParticipation(object):
    principal = 'foobar'
    interaction = None

def setUp(test):
    setup.placefulSetUp()
    zope.security.management.getInteraction().add(TestParticipation())
    xmlconfig.string("""
    <configure xmlns="http://namespaces.zope.org/zope">
    <include package="zope.app" file="meta.zcml" />
    <include package="zope.app.schema" file="meta.zcml" />
    <include package="zope.app.security" file="meta.zcml" />
    <include package="zope.app.component" file="meta.zcml" />
    <include package="zope.app.security" />
    <include package="zope.app.component" />
    <include package="zorg.table" file="adapters.zcml"/>

    <include package="zope.app.form.browser"/>
    </configure>
    """)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../browser/directives.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
