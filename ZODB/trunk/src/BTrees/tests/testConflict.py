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
import sys, os, time, random
execfile(os.path.join(sys.path[0], 'framework.py'))

from BTrees.OOBTree import OOBTree, OOBucket, OOSet, OOTreeSet
from BTrees.IOBTree import IOBTree, IOBucket, IOSet, IOTreeSet
from BTrees.IIBTree import IIBTree, IIBucket, IISet, IITreeSet
from BTrees.OIBTree import OIBTree, OIBucket, OISet, OITreeSet
from unittest import TestCase, TestSuite, TextTestRunner, makeSuite

class Base:
    """ Tests common to all types: sets, buckets, and BTrees """
    def tearDown(self):
        self.t = None
        del self.t

    def _getRoot(self):
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        n = 'fs_tmp__%s' % os.getpid()
        s = FileStorage(n)
        db = DB(s)
        root = db.open().root()
        return root

    def _closeDB(self, root):
        root._p_jar._db.close()
        root = None

    def _delDB(self):
        os.system('rm fs_tmp__*')

class MappingBase(Base):
    """ Tests common to mappings (buckets, btrees) """

    def _deletefail(self):
        del self.t[1]

    def _setupConflict(self):
        base=self.t
        d={}
        for i in range(20):
            d[random.randrange(-10000, 10001)]=i*100000

        e1={}
        while len(e1) < 5:
            k=random.randrange(-10000, 10001)
            if not d.has_key(k):
                e1[k]=len(e1)
        e1=e1.items()

        e2={}
        while len(e2) < 5:
            k=random.randrange(-10000, 10001)
            if not d.has_key(k) and not e2.has_key(k):
                e2[k]=len(e2)
        e2=e2.items()

        base.update(d)
        b1=base.__class__(base)
        b2=base.__class__(base)
        bm=base.__class__(base)

        items=base.items()

        return  base, b1, b2, bm, e1, e2, items

    def testMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        del b2[items[5][0]]
        del b1[items[-1][0]]
        del b2[items[-2][0]]
        del bm[items[0][0]]
        del bm[items[5][0]]
        del bm[items[-1][0]]
        del bm[items[-2][0]]
        test_merge(base, b1, b2, bm, 'merge  delete')

    def testMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        b2[items[5][0]]=1
        del b1[items[-1][0]]
        b2[items[-2][0]]=2
        del bm[items[0][0]]
        bm[items[5][0]]=1
        del bm[items[-1][0]]
        bm[items[-2][0]]=2
        test_merge(base, b1, b2, bm, 'merge update and delete')

    def testMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[items[0][0]]=1
        b2[items[5][0]]=2
        b1[items[-1][0]]=3
        b2[items[-2][0]]=4
        bm[items[0][0]]=1
        bm[items[5][0]]=2
        bm[items[-1][0]]=3
        bm[items[-2][0]]=4
        test_merge(base, b1, b2, bm, 'merge update')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        del b2[items[0][0]]
        test_merge(base, b1, b2, bm, 'merge conflicting delete',
                   should_fail=1)

    def testFailMergeUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[items[0][0]]=1
        b2[items[0][0]]=2
        test_merge(base, b1, b2, bm, 'merge conflicting update',
                   should_fail=1)

    def testFailMergeDeleteAndUpdate(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        del b1[items[0][0]]
        b2[items[0][0]]=-9
        test_merge(base, b1, b2, bm, 'merge conflicting update and delete',
                   should_fail=1)
        
    def testMergeInserts(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1[-99999]=-99999
        b1[e1[0][0]]=e1[0][1]
        b2[99999]=99999
        b2[e1[2][0]]=e1[2][1]

        bm[-99999]=-99999
        bm[e1[0][0]]=e1[0][1]
        bm[99999]=99999
        bm[e1[2][0]]=e1[2][1]
        test_merge(base, b1, b2, bm, 'merge insert')
        
    def testMergeInsertsFromEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        base.clear()
        b1.clear()
        b2.clear()
        bm.clear()

        b1.update(e1)
        bm.update(e1)
        b2.update(e2)
        bm.update(e2)

        test_merge(base, b1, b2, bm, 'merge insert from empty')
        
    def testMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        test_merge(base, b1, b2, bm, 'merge insert from empty')
        
    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        test_merge(base, b1, b2, bm, 'empty one and not other')

    def testFailMergeInsert(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1[-99999]=-99999
        b1[e1[0][0]]=e1[0][1]
        b2[99999]=99999
        b2[e1[0][0]]=e1[0][1]
        test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                   should_fail=1)
        

class NormalSetTests(Base):
    """ Test common to all set types """



class ExtendedSetTests(NormalSetTests):
    "Set (as opposed to TreeSet) specific tests."

    def _setupConflict(self):
        base=self.t
        d={}
        for i in range(20):
            d[random.randrange(-10000, 10001)]=i*100000

        e1={}
        while len(e1) < 5:
            k=random.randrange(-10000, 10001)
            if not d.has_key(k):
                e1[k]=len(e1)
        e1=e1.keys()

        e2={}
        while len(e2) < 5:
            k=random.randrange(-10000, 10001)
            if not d.has_key(k) and not e2.has_key(k):
                e2[k]=len(e2)
        e2=e2.keys()

        base.update(d.keys())
        b1=base.__class__(base)
        b2=base.__class__(base)
        bm=base.__class__(base)

        items=base.keys()

        return  base, b1, b2, bm, e1, e2, items

    def testMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.remove(items[0])
        b2.remove(items[5])
        b1.remove(items[-1])
        b2.remove(items[-2])
        bm.remove(items[0])
        bm.remove(items[5])
        bm.remove(items[-1])
        bm.remove(items[-2])
        test_merge(base, b1, b2, bm, 'merge  delete')

    def testFailMergeDelete(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.remove(items[0])
        b2.remove(items[0])
        test_merge(base, b1, b2, bm, 'merge conflicting delete',
                   should_fail=1)
        
    def testMergeInserts(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.insert(-99999)
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[2])

        bm.insert(-99999)
        bm.insert(e1[0])
        bm.insert(99999)
        bm.insert(e1[2])
        test_merge(base, b1, b2, bm, 'merge insert')
        
    def testMergeInsertsFromEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        base.clear()
        b1.clear()
        b2.clear()
        bm.clear()

        b1.update(e1)
        bm.update(e1)
        b2.update(e2)
        bm.update(e2)

        test_merge(base, b1, b2, bm, 'merge insert from empty')
        
    def testMergeEmptyAndFill(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()
        b2.update(e2)
        bm.update(e2)

        test_merge(base, b1, b2, bm, 'merge insert from empty')
        
    def testMergeEmpty(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()

        b1.clear()
        bm.clear()

        test_merge(base, b1, b2, bm, 'empty one and not other')

    def testFailMergeInsert(self):
        base, b1, b2, bm, e1, e2, items = self._setupConflict()
        b1.insert(-99999)
        b1.insert(e1[0])
        b2.insert(99999)
        b2.insert(e1[0])
        test_merge(base, b1, b2, bm, 'merge conflicting inserts',
                   should_fail=1)
        

def test_merge(o1, o2, o3, expect, message='failed to merge', should_fail=0):
    s1=o1.__getstate__()
    s2=o2.__getstate__()
    s3=o3.__getstate__()
    expected=expect.__getstate__()
    if expected is None: expected=((((),),),)

    if should_fail:
        try: merged=o1._p_resolveConflict(s1, s2, s3)
        except: pass # cool
        else: assert 0, message
    else:
        merged=o1._p_resolveConflict(s1, s2, s3)
        assert merged==expected, message
        
class BucketTests(MappingBase):
    """ Tests common to all buckets """
        

    

class BTreeTests(MappingBase):
    """ Tests common to all BTrees """

## BTree tests

class TestIOBTrees(BTreeTests, TestCase):
    def setUp(self):
        self.t = IOBTree()

class TestOOBTrees(BTreeTests, TestCase):
    def setUp(self):
        self.t = OOBTree()

class TestOIBTrees(BTreeTests, TestCase):
    def setUp(self):
        self.t = OIBTree()

class TestIIBTrees(BTreeTests, TestCase):
    def setUp(self):
        self.t = IIBTree()

## Set tests

class TestIOSets(ExtendedSetTests, TestCase):
    def setUp(self):
        self.t = IOSet()

class TestOOSets(ExtendedSetTests, TestCase):
    def setUp(self):
        self.t = OOSet()

class TestIISets(ExtendedSetTests, TestCase):
    def setUp(self):
        self.t = IISet()

class TestOISets(ExtendedSetTests, TestCase):
    def setUp(self):
        self.t = OISet()

class TestIOTreeSets(NormalSetTests, TestCase):
    def setUp(self):
        self.t = IOTreeSet()
        
class TestOOTreeSets(NormalSetTests, TestCase):
    def setUp(self):
        self.t = OOTreeSet()

class TestIITreeSets(NormalSetTests, TestCase):
    def setUp(self):
        self.t = IITreeSet()

class TestOITreeSets(NormalSetTests, TestCase):
    def setUp(self):
        self.t = OITreeSet()
        
## Bucket tests

class TestIOBuckets(BucketTests, TestCase):
    def setUp(self):
        self.t = IOBucket()

class TestOOBuckets(BucketTests, TestCase):
    def setUp(self):
        self.t = OOBucket()

class TestIIBuckets(BucketTests, TestCase):
    def setUp(self):
        self.t = IIBucket()

class TestOIBuckets(BucketTests, TestCase):
    def setUp(self):
        self.t = OIBucket()

def test_suite():
    TIOBTree = makeSuite(TestIOBTrees, 'test')
    TOOBTree = makeSuite(TestOOBTrees, 'test')
    TOIBTree = makeSuite(TestOIBTrees, 'test')
    TIIBTree = makeSuite(TestIIBTrees, 'test')

    TIOSet = makeSuite(TestIOSets, 'test')
    TOOSet = makeSuite(TestOOSets, 'test')
    TOISet = makeSuite(TestIOSets, 'test')
    TIISet = makeSuite(TestOOSets, 'test')

    TIOTreeSet = makeSuite(TestIOTreeSets, 'test')
    TOOTreeSet = makeSuite(TestOOTreeSets, 'test')
    TOITreeSet = makeSuite(TestIOTreeSets, 'test')
    TIITreeSet = makeSuite(TestOOTreeSets, 'test')

    TIOBucket = makeSuite(TestIOBuckets, 'test')
    TOOBucket = makeSuite(TestOOBuckets, 'test')
    TOIBucket = makeSuite(TestOIBuckets, 'test')
    TIIBucket = makeSuite(TestIIBuckets, 'test')
    
    alltests = TestSuite((TIOSet, TOOSet, TOISet, TIISet,
                          TIOTreeSet, TOOTreeSet, TOITreeSet, TIITreeSet,
                          TIOBucket, TOOBucket, TOIBucket, TIIBucket,
                          TOOBTree, TIOBTree, TOIBTree, TIIBTree))

    return alltests

## utility functions

def lsubtract(l1, l2):
   l1=list(l1)
   l2=list(l2)
   l = filter(lambda x, l1=l1: x not in l1, l2)
   l = l + filter(lambda x, l2=l2: x not in l2, l1)
   return l

def realseq(itemsob):
    return map(lambda x: x, itemsob)

framework()
