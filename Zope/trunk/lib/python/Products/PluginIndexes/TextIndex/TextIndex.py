##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

"""Text Index

"""

__version__ = '$Revision: 1.16 $'[11:-2]


import string, re
import operator,warnings
from Globals import Persistent,DTMLFile
from zLOG import LOG, ERROR
from OFS.SimpleItem import SimpleItem
from Acquisition import Implicit
from Products.PluginIndexes.common.ResultList import ResultList
from Products.PluginIndexes import PluggableIndex       
from Products.PluginIndexes.common.util import parseIndexRequest

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.IIBTree import IIBTree, IIBucket, IISet, IITreeSet
from BTrees.IIBTree import difference, weightedIntersection

from Lexicon import Lexicon

from types import *

class Op:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    __str__ = __repr__

AndNot      = Op('andnot')
And         = Op('and')
Or          = Op('or')
Near        = Op('...')
QueryError  = 'TextIndex.QueryError'
operator_dict = {'andnot': AndNot, 'and': And, 'or': Or,
                 '...': Near, 'near': Near,
                 AndNot: AndNot, And: And, Or: Or, Near: Near}

class TextIndex(PluggableIndex.PluggableIndex, Persistent,
     Implicit, SimpleItem):
    """Full-text index.

    There is a ZCatalog UML model that sheds some light on what is
    going on here.  '_index' is a BTree which maps word ids to mapping
    from document id to score.  Something like:

      {'bob' : {1 : 5, 2 : 3, 42 : 9}}
      {'uncle' : {1 : 1}}


    The '_unindex' attribute is a mapping from document id to word
    ids.  This mapping allows the catalog to unindex an object:

      {42 : ('bob', 'is', 'your', 'uncle')

    This isn't exactly how things are represented in memory, many
    optimizations happen along the way."""

    __implements__ = (PluggableIndex.PluggableIndexInterface,)

    meta_type='TextIndex'

    manage_options= (
        {'label': 'Settings',     
         'action': 'manage_main',
         'help': ('TextIndex','TextIndex_Settings.stx')},
    )

    query_options = ["query","operator"]
 
    def __init__(self, id, ignore_ex=None, call_methods=None, lexicon=None,caller=None,extra=None):
        """Create an index

        The arguments are:

          'id' -- the name of the item attribute to index.  This is
          either an attribute name or a record key.

          'ignore_ex' -- Tells the indexer to ignore exceptions that
          are rasied when indexing an object.

          'call_methods' -- Tells the indexer to call methods instead
          of getattr or getitem to get an attribute.

          'lexicon' is the lexicon object to specify, if None, the
          index will use a private lexicon.

          'caller' -- instance that created the index (maybe None)

          'extra'  -- Record to keep additional parameters

        """

        self.id             = id
        self.ignore_ex      = ignore_ex
        self.call_methods   = call_methods
        self.catalog        = caller


        # Default text index operator (should be visible to ZMI)
        self.useOperator  = 'or'

        self.clear()

        if extra:   self.vocabulary_id = extra.vocabulary
        else:       self.vocabulary_id = "Vocabulary"

        self._lexicon = None

        if lexicon is not None:

            # We need to hold a reference to the lexicon, since we can't
            # really change lexicons.
            self._lexicon = lexicon
            self.vocabulary_id = '__userdefined__'



    def getLexicon(self, vocab_id=None):
        """Return the Lexicon in use. Removed lots of stinking code"""

        if self._lexicon is None:
            ## if no lexicon is provided, create a default one
            try:
                self._lexicon = getattr(self.catalog,self.vocabulary_id).getLexicon()
            except:                
                self._lexicon = Lexicon()
                self.vocabulary_id = '__intern__'

        return self._lexicon



    def __nonzero__(self):
        return not not self._unindex
    

    def clear(self):
        """Reinitialize the text index."""
        self._index   = IOBTree()
        self._unindex = IOBTree()
        self.getLexicon().clear()
        self._lexicon = None

    def _convertBTrees(self, threshold=200):

        if type(self._lexicon) is type(''):
            # Turn the name reference into a hard reference. 
            self._lexicon=self.getLexicon()

        if type(self._index) is IOBTree: return

        from BTrees.convert import convert

        _index=self._index
        self._index=IOBTree()

        def convertScores(scores,
                          type=type, TupleType=TupleType, IIBTree=IIBTree
                          ):
            if type(scores) is not TupleType and type(scores) is not IIBTree():
                scores=IIBTree(scores)
            return scores
                

        convert(_index, self._index, threshold, convertScores)

        _unindex=self._unindex
        self._unindex=IOBTree()
        convert(_unindex, self._unindex, threshold)

    def histogram(self, type=type, TupleType=type(())):
        """Return a mapping which provides a histogram of the number of
        elements found at each point in the index."""

        histogram = IIBucket()
        for (key, value) in self._index.items():
            if type(value) is TupleType: entry=1
            else: entry = len(value)
            histogram[entry] = histogram.get(entry, 0) + 1

        return histogram


    def getEntryForObject(self, rid, default=None):
        """Get all information contained for a specific object.

        This takes the objects record ID as it's main argument."""

        results = self._unindex.get(rid, None)

        if results is None:
            return default
        else:
            return tuple(map(self.getLexicon().getWord,
                             results))
        
            
    def insertForwardIndexEntry(self, entry, documentId, score=1):
        """Uses the information provided to update the indexes.

        The basic logic for choice of data structure is based on
        the number of entries as follows:

            1      tuple
            2-3    dictionary
            4+     bucket.
        """

        index=self._index
        indexRow = index.get(entry, None)

        if indexRow is not None:
            if type(indexRow) is TupleType:
                # Tuples are only used for rows which have only
                # a single entry.  Since we now need more, we'll
                # promote it to a mapping object (dictionary).

                # First, make sure we're not already in it, if so
                # update the score if necessary.
                if indexRow[0] == documentId:
                    if indexRow[1] != score:
                        indexRow = (documentId, score)
                        index[entry] = indexRow
                else:
                    indexRow={
                        indexRow[0]: indexRow[1],
                        documentId: score,
                        }
                    index[entry] = indexRow
            else:
                if indexRow.get(documentId, -1) != score:
                    # score changed (or new entry)
                    
                    if type(indexRow) is DictType:
                        indexRow[documentId] = score
                        if len(indexRow) > 3:
                            # Big enough to give it's own database record
                            indexRow=IIBTree(indexRow) 
                        index[entry] = indexRow
                    else:
                        indexRow[documentId] = score
        else:
            # We don't have any information at this point, so we'll
            # put our first entry in, and use a tuple to save space
            index[entry] = (documentId, score)

    def index_object(self, documentId, obj, threshold=None):
        """ Index an object:
        'documentId' is the integer id of the document
        
        'obj' is the object to be indexed

        'threshold' is the number of words to process between
        commiting subtransactions.  If 'None' subtransactions are
        disabled. """

        # sniff the object for our 'id', the 'document source' of the
        # index is this attribute.  If it smells callable, call it.
        try:
            source = getattr(obj, self.id)
            if callable(source):
                source = str(source())
            else:
                source = str(source)
        except (AttributeError, TypeError):
            return 0
        
        lexicon = self.getLexicon()

        splitter = lexicon.Splitter

        wordScores = OIBTree()
        last = None
        
        # Run through the words and score them
        for word in splitter(source):
            if word[0] == '\"':
                last = self._subindex(word[1:-1], wordScores, last, splitter)
            else:
                if word==last: continue
                last=word
                wordScores[word]=wordScores.get(word,0)+1

        # Convert scores to use wids:
        widScores=IIBucket()
        getWid=lexicon.getWordId
        for word, score in wordScores.items():
            widScores[getWid(word)]=score

        del wordScores

        currentWids=IISet(self._unindex.get(documentId, []))

        # Get rid of document words that are no longer indexed
        self.unindex_objectWids(documentId, difference(currentWids, widScores))
        
        # Now index the words. Note that the new xIBTrees are clever
        # enough to do nothing when there isn't a change. Woo hoo.
        insert=self.insertForwardIndexEntry
        for wid, score in widScores.items():
            insert(wid, documentId, score)

        # Save the unindexing info if it's changed:
        wids=widScores.keys()
        if wids != currentWids.keys():
            self._unindex[documentId]=wids

        return len(wids)

    def _subindex(self, source, wordScores, last, splitter):
        """Recursively handle multi-word synonyms"""
        for word in splitter(source):
            if word[0] == '\"':
                last = self._subindex(word[1:-1], wordScores, last, splitter)
            else:
                if word==last: continue
                last=word
                wordScores[word]=wordScores.get(word,0)+1

        return last

    def unindex_object(self, i): 
        """ carefully unindex document with integer id 'i' from the text
        index and do not fail if it does not exist """
        
        index = self._index
        unindex = self._unindex
        wids = unindex.get(i, None)
        if wids is not None:
            self.unindex_objectWids(i, wids)
            del unindex[i]

    def unindex_objectWids(self, i, wids): 
        """ carefully unindex document with integer id 'i' from the text
        index and do not fail if it does not exist """

        index = self._index
        get=index.get
        for wid in wids:
            widScores = get(wid, None)
            if widScores is None:
                LOG('TextIndex', ERROR,
                    'unindex_object tried to unindex nonexistent'
                    ' document, wid  %s, %s' % (i,wid))
                continue
            if type(widScores) is TupleType:
                del index[wid]
            else:
                try:
                    del widScores[i]
                    if widScores:
                        if type(widScores) is DictType:
                            if len(widScores) == 1:
                                # convert to tuple
                                widScores = widScores.items()[0]
                            index[wid]=widScores
                    else:
                        del index[wid]
                except (KeyError, IndexError, TypeError):
                    LOG('TextIndex', ERROR,
                        'unindex_object tried to unindex nonexistent'
                        ' document %s' % str(i))

    def __getitem__(self, word):
        """Return an InvertedIndex-style result "list"

        Note that this differentiates between being passed an Integer
        and a String.  Strings are looked up in the lexicon, whereas
        Integers are assumed to be resolved word ids. """
        
        if type(word) is IntType:
            # We have a word ID
            result = self._index.get(word, {})
            return ResultList(result, (word,), self)
        else:
            splitSource = tuple(self.getLexicon().Splitter(word))

            if not splitSource:
                return ResultList({}, (word,), self)
        
            if len(splitSource) == 1:
                splitSource = splitSource[0]
                if splitSource[:1] == '"' and splitSource[-1:] == '"':
                    return self[splitSource]

                wids=self.getLexicon().get(splitSource)
                if wids:
                    r = self._index.get(wids[0], None)
                    if r is None:
                        r = {}
                else:
                    r={}

                return ResultList(r, (splitSource,), self)

            r = None
            for word in splitSource:
                rr = self[word]
                if r is None:
                    r = rr
                else:
                    r = r.near(rr)

            return r


    def _apply_index(self, request, cid=''): 
        """ Apply the index to query parameters given in the argument,
        request

        The argument should be a mapping object.

        If the request does not contain the needed parameters, then
        None is returned.
 
        Otherwise two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.  
        """

        record = parseIndexRequest(request,self.id,self.query_options)
        if record.keys==None: return None

        # Changed for 2.4
        # We use the default operator that can me managed via the ZMI

        qop = record.get('operator', self.useOperator)

        # We keep this for pre-2.4 compatibility
        # This stinking code should go away somewhere. A global
        # textindex_operator makes no sense when using multiple
        # text indexes inside a catalog. An index operator should
        # should be specified on a per-index base

        if request.has_key('textindex_operator'):
            qop = request['textindex_operator']
            warnings.warn("The usage of the 'textindex_operator' "
                          "is no longer recommended.\n"
                          "Please use a mapping object and the "
                          "'operator' key to specify the operator.")

        query_operator = operator_dict.get(qop)
        if query_operator is None:
            raise exceptions.RuntimeError, ("Invalid operator '%s' "
                                            "for a TextIndex" % qop)
        r = None

        for key in record.keys:
            key = string.strip(key)
            if not key:
                continue

            b = self.query(key, query_operator).bucket()
            w, r = weightedIntersection(r, b)

        if r is not None:
            return r, (self.id,)
        
        return (IIBucket(), (self.id,))


    def positions(self, docid, words,
                  # This was never tested: obj
                  ):
        """Return the positions in the document for the given document
        id of the word, word."""

        return [1]

        #################################################################
        # The code below here is broken and requires an API change to fix
        # it. Waaaaa.


        if self._schema is None:
            f = getattr
        else:
            f = operator.__getitem__
            id = self._schema[self.id]


        if self.call_methods:
            doc = str(f(obj, self.id)())
        else:
            doc = str(f(obj, self.id))

        r = []
        for word in words:
            r = r+self.getLexicon().Splitter(doc).indexes(word)
        return r



    def query(self, s, default_operator=Or):
        """ Evaluate a query string.
        
        Convert the query string into a data structure of nested lists
        and strings, based on the grouping of whitespace-separated
        strings by parentheses and quotes.  The 'Near' operator is
        inserted between the strings of a quoted group.

        The Lexicon is given the opportunity to transform the
        data structure.  Stemming, wildcards, and translation are
        possible Lexicon services.

        Finally, the query list is normalized so that it and every
        sub-list consist of non-operator strings or lists separated
        by operators. This list is evaluated.
        """

        # First replace any occurences of " and not " with " andnot "
        s = re.sub('(?i)\s+and\s*not\s+', ' andnot ', s)

        # Parse parentheses and quotes
        q = parse(s)

        # Allow the Lexicon to process the query
        q = self.getLexicon().query_hook(q)

        # Insert the default operator between any two search terms not
        # already joined by an operator.
        q = parse2(q, default_operator)

        # evalute the final 'expression'
        return self.evaluate(q)


    def get_operands(self, q, i):
        """Evaluate and return the left and right operands for an operator"""

        try:
            left  = q[i - 1]
            right = q[i + 1]
        except IndexError:
            raise QueryError, "Malformed query"

        operandType = type(left)
        if operandType is IntType:
            left = self[left]
        elif operandType is StringType:
            left = self[left]        
        elif operandType is ListType:
            left = self.evaluate(left)

        operandType = type(right)
        if operandType is IntType:
            right = self[right]
        elif operandType is StringType:
            right = self[right]       
        elif operandType is ListType:
            right = self.evaluate(right)

        return (left, right)



    def evaluate(self, query):
        """Evaluate a parsed query"""
        # Strip off meaningless layers
        while isinstance(query, ListType) and len(query) == 1:
            query = query[0]

        # If it's not a list, assume a string or number
        if not isinstance(query, ListType):
            return self[query]

        # Now we need to loop through the query and reduce
        # operators.  They are currently evaluated in the following
        # order: AndNot -> And -> Or -> Near
        i = 0
        while (i < len(query)):
            if query[i] is AndNot:
                left, right = self.get_operands(query, i)
                val = left.and_not(right)
                query[(i - 1) : (i + 2)] = [ val ]
            else: i = i + 1

        i = 0
        while (i < len(query)):
            if query[i] is And:
                left, right = self.get_operands(query, i)
                val = left & right
                query[(i - 1) : (i + 2)] = [ val ]
            else: i = i + 1

        i = 0
        while (i < len(query)):
            if query[i] is Or:
                left, right = self.get_operands(query, i)
                val = left | right
                query[(i - 1) : (i + 2)] = [ val ]
            else: i = i + 1

        i = 0
        while (i < len(query)):
            if query[i] is Near:
                left, right = self.get_operands(query, i)
                val = left.near(right)
                query[(i - 1) : (i + 2)] = [ val ]
            else: i = i + 1

        if (len(query) != 1):
            raise QueryError, "Malformed query"

        return query[0]


    def numObjects(self):
        """ return number of index objects """
        return len(self._index)


    def manage_setPreferences(self,vocabulary,
                               REQUEST=None,RESPONSE=None,URL2=None):
        """ preferences of TextIndex """


        if self.vocabulary_id != vocabulary:
            self.clear()
            self.vocabulary_id    = vocabulary

        if RESPONSE:
            RESPONSE.redirect(URL2 + '/manage_main?manage_tabs_message=Preferences%20saved')


    manage_workspace  = DTMLFile("dtml/manageTextIndex",globals())
    manage_vocabulary = DTMLFile("dtml/manageVocabulary",globals())

def parse(s):
    """Parse parentheses and quotes"""
    l = []
    tmp = string.lower(s)

    p = parens(tmp)
    while p is not None:
        # Look for quotes in the section of the string before
        # the parentheses, then parse the string inside the parens
        l = l + quotes(p[0])
        l.append(parse(p[1]))

        # continue looking through the rest of the string
        tmp = p[2]
        p = parens(tmp)

    return l + quotes(tmp)

def parse2(q, default_operator, operator_dict=operator_dict):
    """Find operators and operands"""
    isop = operator_dict.has_key
    i = 0
    while i < len(q):
        e = q[i]
        if isinstance(e, ListType):
            q[i] = parse2(e, default_operator)
            if i % 2:
                q.insert(i, default_operator)
                i = i + 1
        elif i % 2:
            # This element should be an operator
            if isop(e):
                # Ensure that it is identical, not merely equal.
                q[i] = operator_dict[e]
            else:
                # Insert the default operator.
                q.insert(i, default_operator)
                i = i + 1
        i = i + 1

    return q


def parens(s, parens_re=re.compile('[()]').search):
    mo = parens_re(s)
    if mo is None:
        return
    
    open_index = mo.start(0) + 1
    paren_count = 0
    while mo is not None:
        index = mo.start(0)
    
        if s[index] == '(':
            paren_count = paren_count + 1
        else:
            paren_count = paren_count - 1
            if paren_count == 0:
                return (s[:open_index - 1], s[open_index:index],
                        s[index + 1:])
            if paren_count < 0:
                break
        mo = parens_re(s, index + 1)

    raise QueryError, "Mismatched parentheses"      


def quotes(s):
    split=string.split
    if '"' not in s:
        return split(s)
    
    # split up quoted regions
    splitted = re.split('\s*\"\s*', s)

    if (len(splitted) % 2) == 0: raise QueryError, "Mismatched quotes"
    
    for i in range(1,len(splitted),2):
        # split the quoted region into words
        words = splitted[i] = split(splitted[i])
        
        # put the Proxmity operator in between quoted words
        j = len(words) - 1
        while j > 0:
            words.insert(j, Near)
            j = j - 1

    i = len(splitted) - 1
    while i >= 0:
        # split the non-quoted region into words
        splitted[i:i+1] = split(splitted[i])
        i = i - 2

    return filter(None, splitted)


manage_addTextIndexForm = DTMLFile('dtml/addTextIndex', globals())

def manage_addTextIndex(self, id, extra=None, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a text index"""
    return self.manage_addIndex(id, 'TextIndex', extra, REQUEST, RESPONSE, URL3)

