##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Text index wrapper.

This exists to implement IInjection and IQuerying.

$Id: textindexwrapper.py,v 1.2 2002/12/25 14:15:34 jim Exp $
"""

from persistence import Persistent

from zope.textindex.okapiindex import OkapiIndex
from zope.textindex.lexicon import Lexicon
from zope.textindex.lexicon import Splitter, CaseNormalizer, StopWordRemover
from zope.textindex.queryparser import QueryParser
from zope.textindex.nbest import NBest

from zope.textindex.textindexinterfaces import \
     IInjection, IQuerying, IStatistics

class TextIndexWrapper(Persistent):

    __implements__ = (IInjection, IQuerying, IStatistics)

    def __init__(self, lexicon=None, index=None):
        """Provisional constructor.

        This creates the lexicon and index if not passed in."""
        if lexicon is None:
            lexicon = Lexicon(Splitter(), CaseNormalizer(), StopWordRemover())
        if index is None:
            index = OkapiIndex(lexicon)
        self.lexicon = lexicon
        self.index = index

    # Methods implementing IInjection

    def index_doc(self, docid, text):
        self.index.index_doc(docid, text)
        self._p_changed = 1 # XXX why is this needed?

    def unindex_doc(self, docid):
        self.index.unindex_doc(docid)
        self._p_changed = 1 # XXX why is this needed?

    # Methods implementing IQuerying

    def query(self, querytext, start=0, count=None):
        parser = QueryParser(self.lexicon)
        tree = parser.parseQuery(querytext)
        results = tree.executeQuery(self.index)
        if not results:
            return [], 0
        if count is None:
            count = max(0, len(results) - start)
        chooser = NBest(start + count)
        chooser.addmany(results.items())
        batch = chooser.getbest()
        batch = batch[start:]
        if batch:
            qw = self.index.query_weight(tree.terms())
            # Hack to avoid ZeroDivisionError
            if qw == 0:
                qw = batch[0][1] or 1
            qw *= 1.0
            batch = [(docid, score/qw) for docid, score in batch]
        return batch, len(results)

    # Methods implementing IStatistics

    def documentCount(self):
        """Return the number of documents in the index."""
        return self.index.documentCount()

    def wordCount(self):
        """Return the number of words in the index."""
        return self.index.wordCount()
