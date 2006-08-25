##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Zope Element Tree Support

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.app.component
from zope.configuration import xmlconfig
from zope.app.testing import setup

from interfaces import IEtree
import zope.etree

#
# Setup for Zope etree. 
#

def etreeSetup(test = None):
    setup.placelessSetUp()
    context = xmlconfig.file("meta.zcml", package = zope.app.component)
    xmlconfig.file("zope.etree-configure.zcml", package = zope.etree,
                   context = context)

    etreeEtree = zope.component.getUtility(IEtree)

    if test is not None:
        test.globs["etree"] = etreeEtree
        test.globs["assertXMLEqual"] = assertXMLEqual
    return etreeEtree

def etreeTearDown(test = None):
    if test is not None:
        del test.globs["etree"]
        del test.globs["assertXMLEqual"]
    etreeEtree = zope.component.getUtility(IEtree)
    zope.component.getGlobalSiteManager().unregisterUtility(etreeEtree)

    setup.placelessTearDown()

#
# Handy methods for testing if two xml fragmenets are equal.
#

def _assertTextEqual(got, expected):
    """
      >>> _assertTextEqual(None, "\\n")
      True

      >>> _assertTextEqual("\\n", "\\n")
      True

      >>> _assertTextEqual("test", "test")
      True

    """
    tgot = got and got.strip()
    texpected = expected and expected.strip()

    error_msg = "'%r != %r' have different element content." %(
        got, expected)

    if not tgot:
        assert not texpected, error_msg
        return True

    if not texpected:
        assert not tgot, error_msg
        return True

    assert isinstance(tgot, (str, unicode)), error_msg
    assert isinstance(texpected, (str, unicode)), error_msg

    assert tgot == texpected, error_msg

    return True

def _assertXMLElementEqual(got, expected):
    etree = zope.component.getUtility(IEtree)

    assert got.tag == expected.tag, \
           "'%r != %r' different tag name." %(got.tag, expected.tag)
    assert len(got) == len(expected), \
           "'%d != %d' different number of subchildren on %r." %(
               len(got), len(expected), got.tag)
    _assertTextEqual(got.text, expected.text)

    for index in range(0, len(got)):
        _assertXMLElementEqual(got[index], expected[index])


def assertXMLEqual(got, expected):
    """
      >>> assertXMLEqual('<test>xml</test>', '<test>xml</test>')

      >>> assertXMLEqual('<test>xml</test>', '<test>xml1</test>')
      Traceback (most recent call last):
      ...
      AssertionError: ''xml' != 'xml1'' have different element content.

      >>> assertXMLEqual('<test><subtest>Test</subtest></test>',
      ...                '<test>Test</test>')
      Traceback (most recent call last):
      ...
      AssertionError: '1 != 0' different number of subchildren on 'test'.

      >>> assertXMLEqual('<test1/>', '<test2/>')
      Traceback (most recent call last):
      ...
      AssertionError: ''test1' != 'test2'' different tag name.

      >>> assertXMLEqual('<a><b><c /></b></a>', '<a><b><c/></b></a>')

    """
    etree = zope.component.getUtility(IEtree)

    if isinstance(got, (str, unicode)):
        got = etree.fromstring(got)
    if isinstance(expected, (str, unicode)):
        expected = etree.fromstring(expected)

    if getattr(got, "getroot", None) is not None:
        # XXX - is this all neccessary.
        got = got.getroot()

        assert getattr(expected, "getroot", None) is not None
        expected = expected.getroot()

    _assertXMLElementEqual(got, expected)
