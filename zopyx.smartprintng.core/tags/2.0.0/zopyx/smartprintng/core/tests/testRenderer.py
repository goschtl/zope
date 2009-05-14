##########################################################################
# zopyx.smartprintng.core 
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import os
import unittest

from zope.interface import implements, Interface
from zope.interface.verify import verifyClass
from zope.app.testing import ztapi

from zopyx.smartprintng.core.renderer import Renderer
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher

html = """
<h1>This is a test</h1>
<img src="http://www.google.it/intl/en/logos/Logo_40wht.gif" />
"""

template_filename = os.path.join(os.path.dirname(__file__), 'test.pt')

class IDummyContext(Interface):
    pass

class DummyContext(object):
    implements(IDummyContext)


class RendererTests(unittest.TestCase):

    def setUp(self):
        self.renderer = Renderer(context=DummyContext())
        ztapi.provideAdapter(IDummyContext, IImageFetcher, ExternalImageFetcher)

    def testRendererWithImageWhichWillFailIfYouAreOffline(self):

        result_html = self.renderer.render(html=html,
                                           template=template_filename,
                                           )

        self.assertEqual('<html>' in result_html, True)
        self.assertEqual('<body>' in result_html, True)
        self.assertEqual('</body>' in result_html, True)
        self.assertEqual('</html>' in result_html, True)
        self.assertEqual('<img' in result_html, True)

    def testRendererWithImageRemover(self):

        result_html = self.renderer.render(html=html,
                                           template=template_filename,
                                           transformations=['zopyx.smartprintng.imageremover',],
                                           )

        self.assertEqual('<img' in result_html, False)

    def testRendererWithNonExistingTransformation(self):
        self.assertRaises(ValueError, self.renderer.render,
                                      html=html,
                                      template=template_filename,
                                      transformations=['non.existing.transformation',],
                                      )



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RendererTests))
    return suite

