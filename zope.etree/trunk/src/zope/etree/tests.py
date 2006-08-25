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
"""
Test the ElementTree support within WebDAV. These aren't really tests but
more of an assertion that I spelt things, like variable names correctly. By
just calling the methods here I have managed to find a bunch of bugs. :-)

Otherwise I just assume that underlying engine does its job correctly.

$Id$
"""

import unittest
import doctest
from cStringIO import StringIO

from zope.interface.verify import verifyObject
from zope import component
from zope.etree import etree
from interfaces import IEtree
from testing import etreeSetup, etreeTearDown


class BaseEtreeTestCase(unittest.TestCase):

    def test_interface(self):
        self.assertEqual(verifyObject(IEtree, self.etree), True)

    def test_comment(self):
        comment = self.etree.Comment(u"some text")

    def test_etree(self):
        etree = self.etree.ElementTree()

    def test_XML(self):
        xml = self.etree.XML(u"<p>some text</p>")

    def test_fromstring(self):
        xml = self.etree.fromstring(u"<p>some text</p>")

    def test_element(self):
        elem = self.etree.Element(u"testtag")

    def test_iselement(self):
        elem = self.etree.Element(u"testtag")
        iselem = self.etree.iselement(elem)
        self.assert_(iselem, "Not an element")

    def test_parse(self):
        f = StringIO("<b>Test Source String</b>")
        self.etree.parse(f)

    def test_qname(self):
        qname = self.etree.QName("http://example.namespace.org", "test")

    def test_tostring(self):
        elem = self.etree.Element(u"testtag")
        string = self.etree.tostring(elem, "ascii")
        self.assert_(isinstance(string, str), "Not a string")

    def test_treeBuilder(self):
        self.assertRaises(NotImplementedError, self.etree.TreeBuilder)

    def test_subelement(self):
        elem = self.etree.Element(u"testtag")
        subel = self.etree.SubElement(elem, "foo")

    def test_PI(self):
        pi = self.etree.PI("sometarget")

    def test_processinginstructions(self):
        pi = self.etree.ProcessingInstruction("sometarget")

    def test_xmltreebulider(self):
        builder = self.etree.XMLTreeBuilder()


class OrigElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from zope.etree.etree import EtreeEtree
        self.etree = EtreeEtree()

    def tearDown(self):
        del self.etree


class LXMLElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from zope.etree.etree import LxmlEtree
        self.etree = LxmlEtree()

    def tearDown(self):
        del self.etree

    def test_PI(self):
        self.assertRaises(NotImplementedError, self.etree.PI, "sometarget")

    def test_processinginstructions(self):
        self.assertRaises(NotImplementedError,
                          self.etree.ProcessingInstruction, "sometarget")

    def test_xmltreebulider(self):
        self.assertRaises(NotImplementedError, self.etree.XMLTreeBuilder)

    def test_namespaces(self):
        # When we have a element whoes namespace declaration is declared
        # in a parent element lxml doesn't print out the namespace
        # declaration by default.
        multinselemstr = """<D:prop xmlns:D="DAV:"><D:owner><H:href xmlns:H="examplens">http://example.org</H:href></D:owner></D:prop>"""
        multinselem = self.etree.fromstring(multinselemstr)
        self.assertEqual(self.etree.tostring(multinselem[0]),
                         """<D:owner xmlns:D="DAV:"><H:href xmlns:H="examplens">http://example.org</H:href></D:owner>""")


class Python25ElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from zope.etree.etree import EtreePy25
        self.etree = EtreePy25()

    def tearDown(self):
        del self.etree


class NoElementTreePresentTestCase(unittest.TestCase):
    # If no element tree engine exists then run this test case. Which will
    # mark the current instance has broken.

    def test_warn(self):
        self.fail("""
        WARNING: zope.etree needs ElementTree installed in order to run.
        """)


class doctestSetup(object):

    def __init__(self, etree):
        self.etree = etree

    def __call__(self, test):
        component.getGlobalSiteManager().registerUtility(self.etree)
        test.globs["etree"] = self.etree


def doctestTeardown(test):
    component.getGlobalSiteManager().unregisterUtility(test.globs["etree"])
    del test.globs["etree"]


def test_suite():
    suite = unittest.TestSuite()

    # Only run the tests for each elementtree that is installed.
    foundetree = False
    try:
        import elementtree
        suite.addTest(unittest.makeSuite(OrigElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "zope.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestSetup(etree.EtreeEtree()),
            tearDown = doctestTeardown))
        foundetree = True
    except ImportError:
        pass

    try:
        import lxml.etree
        suite.addTest(unittest.makeSuite(LXMLElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "zope.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestSetup(etree.LxmlEtree()),
            tearDown = doctestTeardown))
        foundetree = True
    except ImportError:
        pass

    try:
        import xml.etree
        suite.addTest(unittest.makeSuite(Python25ElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "zope.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestSetup(etree.EtreePy25()),
            tearDown = doctestTeardown))
        foundetree = True
    except ImportError:
        pass

    if not foundetree:
        suite.addTest(unittest.makeSuite(NoElementTreePresentTestCase))
    else:
        # rerun the current testing doctest using the default setUp
        suite.addTest(doctest.DocTestSuite(
            "zope.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = etreeSetup,
            tearDown = etreeTearDown))

        # run the README tests to make the documentation does something
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = "zope.etree"))

    return suite
