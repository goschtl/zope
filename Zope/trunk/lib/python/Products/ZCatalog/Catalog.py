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

from Persistence import Persistent
import Acquisition
import ExtensionClass
from SearchIndex import UnIndex, UnTextIndex, UnKeywordIndex, Query
from SearchIndex.Lexicon import Lexicon
import regex, pdb
from MultiMapping import MultiMapping
from string import lower
import Record
from Missing import MV
from zLOG import LOG, ERROR

from Lazy import LazyMap, LazyFilter, LazyCat
from CatalogBrains import AbstractCatalogBrain, NoBrainer

from BTrees.IIBTree import intersection, weightedIntersection
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
import BTrees.Length
from SearchIndex.randid import randid

import time

def orify(seq,
          query_map={
              type(regex.compile('')): Query.Regex,
              type(''): Query.String,
              }):
    subqueries=[]
    for q in seq:
        try: q=query_map[type(q)](q)
        except KeyError: q=Query.Cmp(q)
        subqueries.append(q)
    return apply(Query.Or,tuple(subqueries))
    

class Catalog(Persistent, Acquisition.Implicit, ExtensionClass.Base):
    """ An Object Catalog

    An Object Catalog maintains a table of object metadata, and a
    series of manageable indexes to quickly search for objects
    (references in the metadata) that satisfy a search query.

    This class is not Zope specific, and can be used in any python
    program to build catalogs of objects.  Note that it does require
    the objects to be Persistent, and thus must be used with ZODB3.
    """

    _v_brains = NoBrainer

    def __init__(self, vocabulary=None, brains=None):

        self.schema = {}    # mapping from attribute name to column number
        self.names = ()     # sequence of column names
        self.indexes = {}   # maping from index name to index object

        # The catalog maintains a BTree of object meta_data for
        # convenient display on result pages.  meta_data attributes
        # are turned into brain objects and returned by
        # searchResults.  The indexing machinery indexes all records
        # by an integer id (rid).  self.data is a mapping from the
        # integer id to the meta_data, self.uids is a mapping of the
        # object unique identifier to the rid, and self.paths is a
        # mapping of the rid to the unique identifier.

        self.__len__=BTrees.Length.Length()
        self.clear()

        # indexes can share a lexicon or have a private copy.  Here,
        # we instantiate a lexicon to be shared by all text indexes.
        # This may change.

        if type(vocabulary) is type(''):
            self.lexicon = vocabulary
        else:
            self.lexicon = Lexicon()

        if brains is not None:
            self._v_brains = brains
            
        self.updateBrains()

    def clear(self):
        """ clear catalog """
        
        self.data  = IOBTree()  # mapping of rid to meta_data
        self.uids  = OIBTree()  # mapping of uid to rid
        self.paths = IOBTree()  # mapping of rid to uid

        # convert old-style Catalog object to new in-place
        try: self.__len__.set(0)
        except AttributeError: self.__len__=BTrees.Length.Length()

        for x in self.indexes.values():
            x.clear()

    def _convertBTrees(self, threshold=200):

        from BTrees.convert import convert

        if type(self.data) is not IOBTree:
            data=self.data
            self.data=IOBTree()
            convert(data, self.data, threshold)

            self.__len__=BTrees.Length.Length(len(data))

            uids=self.uids
            self.uids=OIBTree()
            convert(uids, self.uids, threshold)

            paths=self.paths
            self.paths=IOBTree()
            convert(paths, self.paths, threshold)


        for index in self.indexes.values():
            if hasattr(index, '__of__'): index=index.__of__(self)
            index._convertBTrees(threshold)

        lexicon=self.lexicon
        if type(lexicon) is type(''):
           lexicon=getattr(self, lexicon).lexicon
        lexicon._convertBTrees(threshold)

    def __len__(self):
        # NOTE, this is never called for new catalogs, since
        # each instance overrides this.
        return len(self.data)

    def updateBrains(self):
        self.useBrains(self._v_brains)

    def __getitem__(self, index, ttype=type(())):
        """
        Returns instances of self._v_brains, or whatever is passed 
        into self.useBrains.
        """
        if type(index) is ttype:
            # then it contains a score...
            normalized_score, score, key = index
            r=self._v_result_class(self.data[key]).__of__(self.aq_parent)
            r.data_record_id_ = key
            r.data_record_score_ = score
            r.data_record_normalized_score_ = normalized_score
        else:
            # otherwise no score, set all scores to 1
            r=self._v_result_class(self.data[index]).__of__(self.aq_parent)
            r.data_record_id_ = index
            r.data_record_score_ = 1
            r.data_record_normalized_score_ = 1
        return r

    def __setstate__(self, state):
        """ initialize your brains.  This method is called when the
        catalog is first activated (from the persistent storage) """
        Persistent.__setstate__(self, state)
        self.updateBrains()
        if not hasattr(self, 'lexicon'):
            self.lexicon = Lexicon()

    def useBrains(self, brains):
        """ Sets up the Catalog to return an object (ala ZTables) that
        is created on the fly from the tuple stored in the self.data
        Btree.
        """

        class mybrains(AbstractCatalogBrain, brains):
            pass
        
        scopy = self.schema.copy()

        scopy['data_record_id_']=len(self.schema.keys())
        scopy['data_record_score_']=len(self.schema.keys())+1
        scopy['data_record_normalized_score_']=len(self.schema.keys())+2

        mybrains.__record_schema__ = scopy

        self._v_brains = brains
        self._v_result_class = mybrains

    def addColumn(self, name, default_value=None):
        """
        adds a row to the meta data schema
        """
        
        schema = self.schema
        names = list(self.names)

        if schema.has_key(name):
            raise 'Column Exists', 'The column exists'

        if name[0] == '_':
            raise 'Invalid Meta-Data Name', \
                  'Cannot cache fields beginning with "_"'
        
        if not schema.has_key(name):
            if schema.values():
                schema[name] = max(schema.values())+1
            else:
                schema[name] = 0
            names.append(name)

        if default_value is None or default_value == '':
            default_value = MV

        for key in self.data.keys():
            rec = list(self.data[key])
            rec.append(default_value)
            self.data[key] = tuple(rec)

        self.names = tuple(names)
        self.schema = schema

        # new column? update the brain
        self.updateBrains()
            
        self.__changed__(1)    #why?
            
    def delColumn(self, name):
        """
        deletes a row from the meta data schema
        """
        names = list(self.names)
        _index = names.index(name)

        if not self.schema.has_key(name):
            LOG('Catalog', ERROR, ('delColumn attempted to delete '
                                   'nonexistent column %s.' % str(name)))
            return

        names.remove(name)

        # rebuild the schema
        i=0; schema = {}
        for name in names:
            schema[name] = i
            i = i + 1

        self.schema = schema
        self.names = tuple(names)

        # update the brain
        self.updateBrains()

        # remove the column value from each record
        for key in self.data.keys():
            rec = list(self.data[key])
            rec.remove(rec[_index])
            self.data[key] = tuple(rec)

    def addIndex(self, name, index_type):
        """Create a new index, of one of the following index_types

        Types: 'FieldIndex', 'TextIndex', 'KeywordIndex'.
        """

        if self.indexes.has_key(name):
            raise 'Index Exists', 'The index specified already exists'

        if name[0] == '_':
            raise 'Invalid Index Name', 'Cannot index fields beginning with "_"'

        # this is currently a succesion of hacks.  Indexes should be
        # pluggable and managable

        indexes = self.indexes
        if index_type == 'FieldIndex':
            indexes[name] = UnIndex.UnIndex(name)
        elif index_type == 'TextIndex':
            lexicon=self.lexicon
            if type(lexicon) is type(''):
                lexicon=getattr(self, lexicon).getLexicon()
                
            indexes[name] = UnTextIndex.UnTextIndex(name, None, None, lexicon)
        elif index_type == 'KeywordIndex':
            indexes[name] = UnKeywordIndex.UnKeywordIndex(name)
        else:
            raise 'Unknown Index Type', (
                "%s invalid - must be one of %s"
                % (index_type, ['FieldIndex', 'TextIndex', 'KeywordIndex'])
                )

        self.indexes = indexes

    def delIndex(self, name):
        """ deletes an index """

        if not self.indexes.has_key(name):
            raise 'No Index', 'The index specified does not exist'

        indexes = self.indexes
        del indexes[name]
        self.indexes = indexes

    # the cataloging API

    def catalogObject(self, object, uid, threshold=None):
        """ 
        Adds an object to the Catalog by iteratively applying it
        all indexes.

        'object' is the object to be cataloged

        'uid' is the unique Catalog identifier for this object

        """
        
        data = self.data

        # meta_data is stored as a tuple for efficiency
        newDataRecord = self.recordify(object)

        index=self.uids.get(uid, None)
        if index is not None:
            # old data
            
            if data.get(index, 0) != newDataRecord:
                # Update the meta-data, if necessary
                data[index] = newDataRecord
                
        else:
            # new data
            
            if type(data) is IOBTree:
                # New style, get radom id
                
                index=getattr(self, '_v_nextid', 0)
                if index%4000 == 0: index = randid()
                while not data.insert(index, newDataRecord):
                    index=randid()

                # We want ids to be somewhat random, but there are
                # advantages for having some ids generated
                # sequentially when many catalog updates are done at
                # once, such as when reindexing or bulk indexing.
                # We allocate ids sequentially using a volatile base,
                # so different threads get different bases. This
                # further reduces conflict and reduces churn in
                # here and it result sets when bulk indexing.
                self._v_nextid=index+1
            else:
                if data:
                    # find the next available unique id
                    index = data.keys()[-1] + 1
                else:
                    index=0
                data[index] = newDataRecord

            try: self.__len__.change(1)
            except AttributeError: pass # No managed length (old-style)
                    
            self.uids[uid] = index
            self.paths[index] = uid
            
        total = 0
        for x in self.indexes.values():
            ## tricky!  indexes need to acquire now, and because they
            ## are in a standard dict __getattr__ isn't used, so
            ## acquisition doesn't kick in, we must explicitly wrap!
            x = x.__of__(self)
            if hasattr(x, 'index_object'):
                blah = x.index_object(index, object, threshold)
                total = total + blah
            else:
                LOG('Catalog', ERROR, ('catalogObject was passed '
                                       'bad index object %s.' % str(x)))

        return total

    def uncatalogObject(self, uid):
        """ 
        Uncatalog and object from the Catalog.  and 'uid' is a unique
        Catalog identifier

        Note, the uid must be the same as when the object was
        catalogued, otherwise it will not get removed from the catalog

        This method should not raise an exception if the uid cannot
        be found in the catalog.

        """
        data = self.data
        uids = self.uids
        paths = self.paths
        indexes = self.indexes
        rid = uids.get(uid, None)

        if rid is not None:
            for x in indexes.values():
                x = x.__of__(self)
                if hasattr(x, 'unindex_object'):
                    x.unindex_object(rid)
            del data[rid]
            del paths[rid]
            del uids[uid]
            try: self.__len__.change(-1)
            except AttributeError: pass # No managed length
        else:
            LOG('Catalog', ERROR, ('uncatalogObject unsuccessfully '
                                   'attempted to uncatalog an object '
                                   'with a uid of %s. ' % uid))
            

    def uniqueValuesFor(self, name):
        """ return unique values for FieldIndex name """
        return self.indexes[name].uniqueValues()

    def hasuid(self, uid):
        """ return the rid if catalog contains an object with uid """
        return self.uids.get(uid)

    def recordify(self, object):
        """ turns an object into a record tuple """
        record = []
        # the unique id is allways the first element
        for x in self.names:
            attr=getattr(object, x, MV)
            if(attr is not MV and callable(attr)): attr=attr()
            record.append(attr)
        return tuple(record)

    def instantiate(self, record):
        r=self._v_result_class(record[1])
        r.data_record_id_ = record[0]
        return r.__of__(self)


    def getMetadataForRID(self, rid):
        record = self.data[rid]
        result = {}
        for (key, pos) in self.schema.items():
            result[key] = record[pos]
        return result

    def getIndexDataForRID(self, rid):
        result = {}
        for (id, index) in self.indexes.items():
            result[id] = index.__of__(self).getEntryForObject(rid, "")
        return result
    
## Searching engine.  You don't really have to worry about what goes
## on below here...  Most of this stuff came from ZTables with tweaks.

    def _indexedSearch(self, args, sort_index, append, used):
        """
        Iterate through the indexes, applying the query to each one.
        """

        rs=None
        data=self.data
        
        if used is None: used={}
        for i in self.indexes.keys():
            index = self.indexes[i].__of__(self)
            if hasattr(index,'_apply_index'):
                r=index._apply_index(args)
                if r is not None:
                    r, u = r
                    for name in u:
                        used[name]=1
                    w, rs = weightedIntersection(rs, r)
                        
        #assert rs==None or hasattr(rs, 'values') or hasattr(rs, 'keys')
        if rs is None:
            # return everything
            if sort_index is None:
                rs=data.items()
                append(LazyMap(self.instantiate, rs, len(self)))
            else:
                try:
                    for k, intset in sort_index.items():
                        append((k,LazyMap(self.__getitem__, intset)))
                except AttributeError:
                    raise ValueError, (
                        "Incorrect index name passed as" 
                        " 'sort_on' parameter.  Note that you may only" 
                        " sort on values for which there is a matching" 
                        " index available.")
        elif rs:
            # this is reached by having an empty result set (ie non-None)
            if sort_index is None and hasattr(rs, 'values'):
                # having a 'values' means we have a data structure with
                # scores.  Build a new result set, sort it by score, reverse
                # it, compute the normalized score, and Lazify it.
                rset = rs.byValue(0) # sort it by score
                max = float(rset[0][0])
                rs = []
                for score, key in rset:
                    # compute normalized scores
                    rs.append(( int((score/max)*100), score, key))
                append(LazyMap(self.__getitem__, rs))
                    
            elif sort_index is None and not hasattr(rs, 'values'):
                # no scores?  Just Lazify.
                if hasattr(rs, 'keys'): rs=rs.keys() 
                append(LazyMap(self.__getitem__, rs))
            else:
                # sort.  If there are scores, then this block is not
                # reached, therefor 'sort-on' does not happen in the
                # context of text index query.  This should probably
                # sort by relevance first, then the 'sort-on' attribute.
                if ((len(rs) / 4) > len(sort_index)):
                    # if the sorted index has a quarter as many keys as
                    # the result set
                    for k, intset in sort_index.items():
                        # We have an index that has a set of values for
                        # each sort key, so we interset with each set and
                        # get a sorted sequence of the intersections.

                        # This only makes sense if the number of
                        # keys is much less then the number of results.
                        intset = intersection(rs, intset)
                        if intset:
                            if hasattr(intset, 'keys'): intset=intset.keys() 
                            append((k,LazyMap(self.__getitem__, intset)))
                else:
                    if hasattr(rs, 'keys'): rs=rs.keys()
                    for did in rs:
                        append((sort_index.keyForDocument(did),
                               LazyMap(self.__getitem__,[did])))

        return used

    def searchResults(self, REQUEST=None, used=None,
                      query_map={
                          type(regex.compile('')): Query.Regex,
                          type([]): orify,
                          type(''): Query.String,
                          }, **kw):

        # Get search arguments:
        if REQUEST is None and not kw:
            try: REQUEST=self.REQUEST
            except AttributeError: pass
        if kw:
            if REQUEST:
                m=MultiMapping()
                m.push(REQUEST)
                m.push(kw)
                kw=m
        elif REQUEST: kw=REQUEST

        # Make sure batch size is set
        if REQUEST and not REQUEST.has_key('batch_size'):
            try: batch_size=self.default_batch_size
            except AttributeError: batch_size=20
            REQUEST['batch_size']=batch_size

        # Compute "sort_index", which is a sort index, or none:
        if kw.has_key('sort-on'):
            sort_index=kw['sort-on']
        elif hasattr(self, 'sort-on'):
            sort_index=getattr(self, 'sort-on')
        elif kw.has_key('sort_on'):
            sort_index=kw['sort_on']
        else: sort_index=None
        sort_order=''
        if sort_index is not None:
            if self.indexes.has_key(sort_index):
                sort_index=self.indexes[sort_index]
                if not hasattr(sort_index, 'keyForDocument'):
                    raise CatalogError(
                        'The index chosen for sort_on is not capable of being'
                        ' used as a sort index.'
                        )
            else:
                raise CatalogError, ('Unknown sort_on index %s' % sort_index)
        
        # Perform searches with indexes and sort_index
        r=[]
        used=self._indexedSearch(kw, sort_index, r.append, used)
        if not r:
            return LazyCat(r)

        # Sort/merge sub-results
        if len(r)==1:
            if sort_index is None: r=r[0]
            else: r=r[0][1]
        else:
            if sort_index is None: r=LazyCat(r)
            else:
                r.sort()
                if kw.has_key('sort-order'):
                    so=kw['sort-order']
                elif hasattr(self, 'sort-order'):
                    so=getattr(self, 'sort-order')
                elif kw.has_key('sort_order'):
                    so=kw['sort_order']
                else: so=None
                if (type(so) is type('') and
                    lower(so) in ('reverse', 'descending')):
                    r.reverse()
                r=LazyCat(map(lambda i: i[1], r))

        return r

    __call__ = searchResults


class CatalogError(Exception): pass
