##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Register protection information for some standard low-level types

Revision information:
$Id: _protections.py,v 1.7 2002/12/20 11:11:37 stevea Exp $
"""

def protect():
    from Zope.Security.Checker import defineChecker, NamesChecker, NoProxy


    # excluding _check, _bucket_type, _firstbucket, and write operations
    _btreeChecker = NamesChecker(['__str__', '__repr__', '__contains__',
                                  '__getitem__', '__iter__', '__len__',  
                                  'byValue', 'get', 'has_key', 'items', 
                                  'iteritems', 'iterkeys', 'itervalues',
                                  'keys', 'maxKey', 'minKey', 'values'])

    # excluding _next
    _btreeBucketChecker = NamesChecker([
            '__contains__', '__getitem__', '__iter__', '__len__', '__repr__',
            '__str__', 'byValue', 'get', 'has_key', 'items', 'iteritems',
            'iterkeys', 'itervalues', 'keys', 'maxKey','minKey', 'values'])
    
    _btreeSetChecker = NamesChecker([
            '__contains__', '__getitem__', '__iter__', '__len__', '__repr__',
            '__str__', 'has_key', 'insert', 'keys', 'maxKey', 'minKey'])
    
    # excluding _bucket_type, _check
    _btreeTreeSetChecker = NamesChecker([
            '__contains__', '__iter__', '__len__', '__repr__',
            '__str__', 'has_key', 'insert', 'keys', 'maxKey', 'minKey'])
    
    _btreeItemsChecker = NamesChecker([
            '__iter__', '__repr__', '__str__', '__getitem__', '__len__',
            '__contains__'])
    
    _iteratorChecker = NamesChecker(['next'])

    from Persistence.BTrees.IIBTree import IIBTree, IIBucket, IISet, IITreeSet
    from Persistence.BTrees.IOBTree import IOBTree, IOBucket, IOSet, IOTreeSet
    from Persistence.BTrees.OIBTree import OIBTree, OIBucket, OISet, OITreeSet
    from Persistence.BTrees.OOBTree import OOBTree, OOBucket, OOSet, OOTreeSet

    _btree_checkers = { 
        IIBTree: _btreeChecker,
        IOBTree: _btreeChecker,
        OIBTree: _btreeChecker,
        OOBTree: _btreeChecker,
        IIBucket: _btreeBucketChecker,
        IOBucket: _btreeBucketChecker,
        OIBucket: _btreeBucketChecker,
        OOBucket: _btreeBucketChecker,
        IISet: _btreeSetChecker,
        IOSet: _btreeSetChecker,
        OISet: _btreeSetChecker,
        OOSet: _btreeSetChecker,
        IITreeSet: _btreeTreeSetChecker,
        IOTreeSet: _btreeTreeSetChecker,
        OITreeSet: _btreeTreeSetChecker,
        OOTreeSet: _btreeTreeSetChecker,
        type(iter(IIBTree())): NoProxy, # II-iterator is a rock
        type(iter(IOBTree())): _iteratorChecker, # IO-iterator
        type(iter(OIBTree())): _iteratorChecker, # OI-iterator
        type(iter(OOBTree())): _iteratorChecker, # OO-iterator
        type(IIBTree().keys()): NoProxy, # IIBTreeItems is a rock
        type(IOBTree().keys()): _btreeItemsChecker, # IOBTreeItems
        type(OIBTree().keys()): _btreeItemsChecker, # OIBTreeItems
        type(OOBTree().keys()): _btreeItemsChecker, # OOBTreeItems
    }
    for which_type, checker in _btree_checkers.iteritems():
        defineChecker(which_type, checker)

    from Persistence.PersistentList import PersistentList

    defineChecker(PersistentList,
                  NamesChecker(
                     ['__getitem__', '__getslice__', '__len__', '__iter__',
                      '__contains__', 'index', 'count'])
                  )

    from Persistence.PersistentDict import PersistentDict

    defineChecker(PersistentDict,
                  NamesChecker(['__getitem__', '__len__', '__iter__',
                        'get', 'has_key', '__copy__',
                        'keys', 'values', 'items',
                        'iterkeys', 'iteritems', 'itervalues', '__contains__',
                        ]
                     )
                  )
    from Persistence import PersistentMetaClass
    from Zope.Security.Checker import _typeChecker
    defineChecker(PersistentMetaClass, _typeChecker)
