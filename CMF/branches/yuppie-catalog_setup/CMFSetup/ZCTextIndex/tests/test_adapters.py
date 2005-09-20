##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZCTextIndex node adapter unit tests.

$Id$
"""

import unittest
import Testing
import Zope2
Zope2.startup()

from Acquisition import Implicit

from Products.CMFSetup.testing import NodeAdapterTestCase


class _extra:

    pass


class DummyCatalog(Implicit):

    pass


_PLEXICON_XML = """\
<object name="foo_plexicon" meta_type="ZCTextIndex Lexicon">
 <element name="Whitespace splitter" group="Word Splitter"/>
 <element name="Case Normalizer" group="Case Normalizer"/>
 <element name="Remove listed stop words only" group="Stop Words"/>
</object>
"""

_ZCTEXT_XML = """\
<index name="foo_zctext" meta_type="ZCTextIndex">
 <indexed_attr value="foo_zctext"/>
 <extra name="index_type" value="Okapi BM25 Rank"/>
 <extra name="lexicon_id" value="foo_plexicon"/>
</index>
"""


class ZCLexiconNodeAdapterTests(NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFSetup.ZCTextIndex.adapters \
                import ZCLexiconNodeAdapter

        return ZCLexiconNodeAdapter

    def _populate(self, obj):
        from Products.ZCTextIndex.Lexicon import CaseNormalizer
        from Products.ZCTextIndex.Lexicon import Splitter
        from Products.ZCTextIndex.Lexicon import StopWordRemover
        obj._pipeline = (Splitter(), CaseNormalizer(), StopWordRemover())

    def setUp(self):
        from Products.ZCTextIndex.ZCTextIndex import PLexicon

        self._obj = PLexicon('foo_plexicon')
        self._XML = _PLEXICON_XML


class ZCTextIndexNodeAdapterTests(NodeAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFSetup.ZCTextIndex.adapters \
                import ZCTextIndexNodeAdapter

        return ZCTextIndexNodeAdapter

    def setUp(self):
        from Products.ZCTextIndex.ZCTextIndex import PLexicon
        from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex

        catalog = DummyCatalog()
        catalog.foo_plexicon = PLexicon('foo_plexicon')
        extra = _extra()
        extra.lexicon_id = 'foo_plexicon'
        extra.index_type='Okapi BM25 Rank'
        self._obj = ZCTextIndex('foo_zctext', extra=extra,
                                caller=catalog).__of__(catalog)
        self._XML = _ZCTEXT_XML


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZCLexiconNodeAdapterTests),
        unittest.makeSuite(ZCTextIndexNodeAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
