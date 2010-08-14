##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Lexicon unit tests.
"""

import unittest

import os
import sys

import transaction
import ZODB


class StupidPipelineElement:

    def __init__(self, fromword, toword):
        self.__fromword = fromword
        self.__toword = toword

    def process(self, seq):
        res = []
        for term in seq:
            if term == self.__fromword:
                res.append(self.__toword)
            else:
                res.append(term)
        return res


class WackyReversePipelineElement:

    def __init__(self, revword):
        self.__revword = revword

    def process(self, seq):
        res = []
        for term in seq:
            if term == self.__revword:
                x = list(term)
                x.reverse()
                res.append(''.join(x))
            else:
                res.append(term)
        return res


class StopWordPipelineElement:

    def __init__(self, stopdict={}):
        self.__stopdict = stopdict

    def process(self, seq):
        res = []
        for term in seq:
            if self.__stopdict.get(term):
                continue
            else:
                res.append(term)
        return res


class LexiconTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZCTextIndex.Lexicon import Lexicon
        return Lexicon

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_interfaces(self):
        from Products.ZCTextIndex.interfaces import ILexicon
        from zope.interface.verify import verifyClass

        verifyClass(ILexicon, self._getTargetClass())

    def testSourceToWordIds(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter())
        wids = lexicon.sourceToWordIds('cats and dogs')
        self.assertEqual(wids, [1, 2, 3])

    def testTermToWordIds(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter())
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('dogs')
        self.assertEqual(wids, [3])

    def testMissingTermToWordIds(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter())
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('boxes')
        self.assertEqual(wids, [0])

    def testTermToWordIdsWithProcess_post_glob(self):
        """This test is for added process_post_glob"""
        from Products.ZCTextIndex.Lexicon import Splitter

        class AddedSplitter(Splitter):
            def process_post_glob(self, lst):
                assert lst == ['dogs']
                return ['dogs']
        lexicon = self._makeOne(AddedSplitter())
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('dogs')
        self.assertEqual(wids, [3])

    def testMissingTermToWordIdsWithProcess_post_glob(self):
        """This test is for added process_post_glob"""
        from Products.ZCTextIndex.Lexicon import Splitter

        class AddedSplitter(Splitter):
            def process_post_glob(self, lst):
                assert lst == ['dogs']
                return ['fox']
        lexicon = self._makeOne(AddedSplitter())
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('dogs')
        self.assertEqual(wids, [0])

    def testOnePipelineElement(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter(),
                                StupidPipelineElement('dogs', 'fish'))
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('fish')
        self.assertEqual(wids, [3])

    def testSplitterAdaptorFold(self):
        from Products.ZCTextIndex.Lexicon import CaseNormalizer
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter(), CaseNormalizer())
        wids = lexicon.sourceToWordIds('CATS and dogs')
        wids = lexicon.termToWordIds('cats and dogs')
        self.assertEqual(wids, [1, 2, 3])

    def testSplitterAdaptorNofold(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter())
        wids = lexicon.sourceToWordIds('CATS and dogs')
        wids = lexicon.termToWordIds('cats and dogs')
        self.assertEqual(wids, [0, 2, 3])

    def testTwoElementPipeline(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter(),
                          StupidPipelineElement('cats', 'fish'),
                          WackyReversePipelineElement('fish'))
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('hsif')
        self.assertEqual(wids, [1])

    def testThreeElementPipeline(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        lexicon = self._makeOne(Splitter(),
                          StopWordPipelineElement({'and':1}),
                          StupidPipelineElement('dogs', 'fish'),
                          WackyReversePipelineElement('fish'))
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('hsif')
        self.assertEqual(wids, [2])

    def testSplitterLocaleAwareness(self):
        import locale
        from Products.ZCTextIndex.Lexicon import Splitter
        from Products.ZCTextIndex.HTMLSplitter import HTMLWordSplitter

        loc = locale.setlocale(locale.LC_ALL) # get current locale
         # set German locale
        try:
            if sys.platform != 'win32':
                locale.setlocale(locale.LC_ALL, 'de_DE.ISO8859-1')
            else:
                locale.setlocale(locale.LC_ALL, 'German_Germany.1252')
        except locale.Error:
            return # This test doesn't work here :-(
        expected = ['m\xfclltonne', 'waschb\xe4r',
                    'beh\xf6rde', '\xfcberflieger']
        words = [" ".join(expected)]
        words = Splitter().process(words)
        self.assertEqual(words, expected)
        words = HTMLWordSplitter().process(words)
        self.assertEqual(words, expected)
        locale.setlocale(locale.LC_ALL, loc) # restore saved locale


class LexiconConflictTests(unittest.TestCase):

    db = None

    def _getTargetClass(self):
        from Products.ZCTextIndex.Lexicon import Lexicon
        return Lexicon

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def tearDown(self):
        if self.db is not None:
            self.db.close()
            self.storage.cleanup()

    def openDB(self):
        from ZODB.DB import DB
        from ZODB.FileStorage import FileStorage

        n = 'fs_tmp__%s' % os.getpid()
        self.storage = FileStorage(n)
        self.db = DB(self.storage)

    def testAddWordConflict(self):
        from Products.ZCTextIndex.Lexicon import Splitter

        self.l = self._makeOne(Splitter())
        self.openDB()
        r1 = self.db.open().root()
        r1['l'] = self.l
        transaction.commit()

        r2 = self.db.open().root()
        copy = r2['l']
        # Make sure the data is loaded
        list(copy._wids.items())
        list(copy._words.items())
        copy.length()

        self.assertEqual(self.l._p_serial, copy._p_serial)

        self.l.sourceToWordIds('mary had a little lamb')
        transaction.commit()

        copy.sourceToWordIds('whose fleece was')
        copy.sourceToWordIds('white as snow')
        transaction.commit()
        self.assertEqual(copy.length(), 11)
        self.assertEqual(copy.length(), len(copy._words))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LexiconTests))
    suite.addTest(unittest.makeSuite(LexiconConflictTests))
    return suite
