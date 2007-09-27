##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Analyze database references
"""

import cPickle, cStringIO, gzip, sys

import ZODB.FileStorage.FileStorage
import ZODB.utils

def oid_repr(oid):
    return hex(ZODB.utils.u64(oid))[2:-1]

def collect(iterator, output):
    """Create a database of database references.

    Return a dictionary mapping oids to dictionaries with keys 'from'
    and 'to' with values that are dictionaries mapping oids to lists
    of references.
    """
    pickler = cPickle.Pickler(gzip.open(output, 'wb'))
    pickler.fast = True
    
    for trans in iterator:
        trandata = trans.tid, trans._tpos
        data = []
        for record in trans:
            refs = []
            u = cPickle.Unpickler(cStringIO.StringIO(record.data))
            u.persistent_load = refs
            u.noload()
            u.noload()
            data.append((record.oid, record.tid, refs))
        pickler.dump((trandata, data))
    
def collect_script(args=None):
    if args is None:
        args = sys.argv[1:]

    while args:
        inp, outp = args.pop(0), args.pop(0)

        iterator = sys.modules['ZODB.FileStorage.FileStorage' # :(
                               ].FileIterator(inp)
        collect(iterator, outp)

def load(fname):
    unpickler = cPickle.Unpickler(gzip.open(fname))
    result = {}
    while 1:
        try:
            trandata, data = unpickler.load()
        except EOFError:
            return result

        for (oid, serial, refs) in data:
            _update(result, trandata, oid, serial, refs)

def load_trans(fname):
    unpickler = cPickle.Unpickler(gzip.open(fname))
    result = {}
    while 1:
        try:
            trandata, data = unpickler.load()
        except EOFError:
            return result

        result.__setitem__(*trandata)

class Entry(object):
    __slots__ = 'from_', 'present' # , '_to'

    def __init__(self):
        self.present = False
        self.from_ = () 

    def __getstate__(self):
        return self.present, self.from_

    def __setstate__(self, state):
       self.present, self.from_ = state

#     def __eq__(self, other):
#         return self.__getstate__() == other.__getstate__()

    def __repr__(self):
        result = ['']
        result.append('present: %s' % self.present)
#         result.append(
#             'to: %s'
#             % ', '.join(map(repr, (sorted(getattr(self, '_to', ()))))))
        result.append(
                'from_: %s'
                % ', '.join(map(repr, sorted(getattr(self, 'from_', ())))))
        result.append('')
        return '\n    '.join(result)
            
        
def _update(result, tinfo, oid, serial, refs):
    """Create a database of database references.

    Return a dictionary mapping oids to dictionaries with keys 'from'
    and 'to' with values that are dictionaries mapping oids to lists
    of references.
    """
    from_oid = oid_repr(oid)
    from_data = result.get(from_oid)
    if from_data is None:
        from_data = result[from_oid] = Entry()
    from_data.present = True

    for ref in refs:
        if isinstance(ref, tuple):
            to_oid = oid_repr(ref[0])
        elif isinstance(ref, str):
            to_oid = oid_repr(ref)
        elif isinstance(ref, list):
            if len(ref) == 1:
                to_oid = oid_repr(ref[0])
            else:
                try:
                    reference_type, args = ref
                except ValueError:
                    print 'wtf', ref
                    continue

                if reference_type == 'w':
                    to_oid = oid_repr(args[0])
                elif reference_type in 'nm':
                    to_oid = args[0], oid_repr(args[1])
                else:
                    print wtf, reference_type, args
        else:
            print 'wtf', ref
            continue

        # from_data.to.add(to_oid)

        to_data = result.get(to_oid)
        if to_data is None:
            to_data = result[to_oid] = Entry()
        if from_oid not in to_data.from_:
            to_data.from_ += (from_oid, )

def references(iterator):
    """Create a database of database references.

    Return a dictionary mapping oids to dictionaries with keys 'from'
    and 'to' with values that are dictionaries mapping oids to lists
    of references.
    """
    result = {}
    for trans in iterator:
        trandata = trans.tid, trans._tpos
        for record in trans:
            refs = []
            u = cPickle.Unpickler(cStringIO.StringIO(record.data))
            u.persistent_load = refs
            u.noload()
            u.noload()
            _update(result, trandata, record.oid, record.tid, refs)
            
    return result

def references_script(args=None):
    if args is None:
        args = sys.argv[1:]

    [inp, outp] = args

    iterator = sys.modules['ZODB.FileStorage.FileStorage' # :(
                           ].FileIterator(inp)
    data = references(iterator)
    cPickle.Pickler(open(outp, 'w'), 1).dump(data)
