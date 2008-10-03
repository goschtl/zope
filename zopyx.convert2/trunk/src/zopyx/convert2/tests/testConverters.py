##########################################################################
# zopyx.convert - XSL-FO related functionalities
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""
Tests, tests, tests.........
"""

import os
import sys
import unittest

from zope.interface.verify import verifyClass
from zopyx.convert2.interfaces import IFOConverter, IHTML2FOConverter, IXSLFOConverter

from zopyx.convert2 import HTML2FOConverter
from zopyx.convert2 import RTFConverter, WMLConverter, DOCXConverter, ODTConverter
from zopyx.convert2 import PDFConverter, Converter


html1 = os.path.join(os.path.dirname(__file__), 'data', 'test1.html')
html2 = os.path.join(os.path.dirname(__file__), 'data', 'test2.html')

class ConverterTests(unittest.TestCase):

    def testInterfaces(self):
        verifyClass(IHTML2FOConverter, HTML2FOConverter)
        verifyClass(IFOConverter, RTFConverter)
        verifyClass(IFOConverter, ODTConverter)
        verifyClass(IFOConverter, DOCXConverter)
        verifyClass(IFOConverter, WMLConverter)
        verifyClass(IXSLFOConverter, Converter)

class RegressionTests(unittest.TestCase):

    def _test(self, converter):

        for filename in (html1, html2):
            fo_filename = HTML2FOConverter().convert(filename)
            try:
                output_filename = converter().convert(fo_filename)
            except: 
                print >>sys.stderr, 'Error converting %s' % filename
                raise

    def testPDF(self):
        return self._test(PDFConverter)

    def testRTF(self):
        return self._test(RTFConverter)

    def testODT(self):
        return self._test(ODTConverter)

    def testWML(self):
        return self._test(WMLConverter)

    def testDOCX(self):
        return self._test(DOCXConverter)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ConverterTests))
    suite.addTest(makeSuite(RegressionTests))
    return suite

