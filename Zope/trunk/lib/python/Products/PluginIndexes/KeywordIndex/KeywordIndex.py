##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from zLOG import LOG, ERROR
from BTrees.OOBTree import OOSet, difference

from Globals import DTMLFile
from Products.PluginIndexes import PluggableIndex

from Products.PluginIndexes.common.UnIndex import UnIndex

class KeywordIndex(UnIndex):

    __implements__ = (PluggableIndex.PluggableIndexInterface,)

    meta_type="KeywordIndex"

    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main',
         'help': ('KeywordIndex','KeywordIndex_Settings.stx')},
    )

    query_options = ["query","operator"]


    """Like an UnIndex only it indexes sequences of items

    Searches match any keyword.

    This should have an _apply_index that returns a relevance score
    """

    def index_object(self, documentId, obj, threshold=None):
        """ index an object 'obj' with integer id 'i'

        Ideally, we've been passed a sequence of some sort that we
        can iterate over. If however, we haven't, we should do something
        useful with the results. In the case of a string, this means
        indexing the entire string as a keyword."""

        # First we need to see if there's anything interesting to look at
        # self.id is the name of the index, which is also the name of the
        # attribute we're interested in.  If the attribute is callable,
        # we'll do so.

        newKeywords = self._get_object_keywords(obj)

        oldKeywords = self._unindex.get(documentId, None)

        if oldKeywords is None:
            # we've got a new document, let's not futz around.
            try:
                for kw in newKeywords:
                    self.insertForwardIndexEntry(kw, documentId)
                self._unindex[documentId] = list(newKeywords)
            except TypeError:
                return 0
        else:
            # we have an existing entry for this document, and we need
            # to figure out if any of the keywords have actually changed
            if type(oldKeywords) is not OOSet:
                oldKeywords = OOSet(oldKeywords)
            newKeywords = OOSet(newKeywords)
            fdiff = difference(oldKeywords, newKeywords)
            rdiff = difference(newKeywords, oldKeywords)
            if fdiff or rdiff:
                # if we've got forward or reverse changes
                self._unindex[documentId] = list(newKeywords)
                if fdiff:
                    self.unindex_objectKeywords(documentId, fdiff)
                if rdiff:
                    for kw in rdiff:
                        self.insertForwardIndexEntry(kw, documentId)
        return 1

    def _get_object_keywords(self,obj):
        newKeywords = getattr(obj, self.id, ())
        if callable(newKeywords):
            newKeywords = newKeywords()
        if hasattr(newKeywords,'capitalize'): # is it string-like ?
            newKeywords = (newKeywords, )
        return newKeywords

    def unindex_objectKeywords(self, documentId, keywords):
        """ carefully unindex the object with integer id 'documentId'"""

        if keywords is not None:
            for kw in keywords:
                self.removeForwardIndexEntry(kw, documentId)

    def unindex_object(self, documentId):
        """ carefully unindex the object with integer id 'documentId'"""

        keywords = self._unindex.get(documentId, None)
        self.unindex_objectKeywords(documentId, keywords)
        try:
            del self._unindex[documentId]
        except KeyError:
            LOG('UnKeywordIndex', ERROR, 'Attempt to unindex nonexistent'
                ' document id %s' % documentId)


    index_html = DTMLFile('dtml/index', globals())
    manage_workspace = DTMLFile('dtml/manageKeywordIndex', globals())



manage_addKeywordIndexForm = DTMLFile('dtml/addKeywordIndex', globals())

def manage_addKeywordIndex(self, id, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a keyword index"""
    return self.manage_addIndex(id, 'KeywordIndex', extra=None, \
              REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
