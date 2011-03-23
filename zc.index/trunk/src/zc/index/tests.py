"""Unit test for zc.index.

"""
__docformat__ = "reStructuredText"

import os.path
import unittest

import zope.file.interfaces
import zope.interface
import zope.component
import zope.mimetype.interfaces
from zope.app.testing import placelesssetup

import doctest

import zc.index.base


here = os.path.dirname(os.path.abspath(__file__))


class SampleFile(object):

    zope.interface.implements(zope.file.interfaces.IFile)

    def __init__(self, filename):
        self.filename = filename

    def open(self, mode="rb"):
        path = os.path.join(here, self.filename)
        return open(path, "rb")

class MockContentInfo(object):
    zope.interface.implements(zope.mimetype.interfaces.IContentInfo)
    zope.component.adapts(zope.file.interfaces.IFile)
    def __init__(self, context):
        self.context = context
        self.effectiveParameters = {'charset': 'ascii'}

    def decode(self, s):
        return unicode(s)

def wordsFromText(text):
    words = set()
    if isinstance(text, basestring):
        text = [text]
    for s in text:
        s = s.replace(",", " ").replace(".", " ")
        for w in s.split():
            words.add(w)
    return words


def test_suite():
    suite = unittest.TestSuite()
    if zc.index.base.haveProgram("wvWare"):
        suite.addTest(doctest.DocFileSuite("msword.txt"))
    if zc.index.base.haveProgram("pdftotext"):
        suite.addTest(doctest.DocFileSuite("pdf.txt"))
    suite.addTest(doctest.DocFileSuite("ooffice.txt"))
    suite.addTest(doctest.DocFileSuite("rtf.txt"))
    suite.addTest(doctest.DocFileSuite("rtflib.txt"))
    suite.addTest(doctest.DocFileSuite(
        "text.txt",
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown))
    suite.addTest(doctest.DocFileSuite(
        "html.txt",
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        encoding='utf-8'))
    suite.addTest(doctest.DocFileSuite(
        "extensiblemarkuplanguage.txt",
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        encoding='utf-8'))
    return suite
