import os

from zope.app.testing import setup
from zope.app.testing.functional import ZCMLLayer
from zope.component import provideAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore

from zopesandbox.document.interfaces import IDocument
from zopesandbox.document.document import DocumentDublinCore 

DocumentLayer = ZCMLLayer(os.path.join(os.path.dirname(__file__), 'ftesting.zcml'), __name__, 'DocumentLayer')

def setUp(test):
    setup.placefulSetUp()
    provideAdapter(DocumentDublinCore, (IDocument,), IWriteZopeDublinCore)

def tearDown(test):
    setup.placefulTearDown()
