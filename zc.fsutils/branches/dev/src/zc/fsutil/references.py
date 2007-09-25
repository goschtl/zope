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

import cPickle, cStringIO, sys

import ZODB.FileStorage.FileStorage
import ZODB.utils


def collect(iterator, output):
    """Create a database of database references.

    Return a dictionary mapping oids to dictionaries with keys 'from'
    and 'to' with values that are dictionaries mapping oids to lists
    of references.
    """
    pickler = cPickle.Pickler(open(output, 'w'))
    pickler.fast = True
    
    for trans in iterator:
        trandata = trans.tid, trans._tpos
        for record in trans:
            refs = []
            u = cPickle.Unpickler(cStringIO.StringIO(record.data))
            u.persistent_load = refs
            u.noload()
            u.noload()
            pickler.dump((trandata, record.oid, record.tid, refs))
    
def collect_script(args=None):
    if args is None:
        args = sys.argv[1:]

    [inp, outp] = args

    iterator = sys.modules['ZODB.FileStorage.FileStorage' # :(
                           ].FileIterator(inp)
    data = collect(iterator, outp)

def load(fname):
    unpickler = cPickle.Unpickler(open(fname))
    result = {}
    while 1:
        try:
            data = unpickler.load()
        except EOFError:
            return result
        _update(result, *data)

        
def _update(result, tinfo, oid, serial, refs):
    """Create a database of database references.

    Return a dictionary mapping oids to dictionaries with keys 'from'
    and 'to' with values that are dictionaries mapping oids to lists
    of references.
    """
    from_oid = ZODB.utils.oid_repr(oid)
    from_data = result.get(from_oid)
    if from_data is None:
        from_data = result[from_oid] = {
            'from': {}, 'to': {}, 'serials': [],
            }
    from_data['serials'].append(serial)

    for ref in refs:
        if isinstance(ref, tuple):
            to_oid = ZODB.utils.oid_repr(ref[0])
        elif isinstance(ref, str):
            to_oid = ZODB.utils.oid_repr(ref)
        elif isinstance(ref, list):
            if len(ref) == 1:
                to_oid = ZODB.utils.oid_repr(ref[0])
            else:
                try:
                    reference_type, args = ref
                except ValueError:
                    print 'wtf', ref
                    continue

                if reference_type == 'w':
                    to_oid = ZODB.utils.oid_repr(args[0])
                elif reference_type in 'nm':
                    to_oid = args[0], ZODB.utils.oid_repr(args[1])
                else:
                    print wtf, reference_type, args
        else:
            print 'wtf', ref
            continue

        ref = dict(ref=ref, tinfo=tinfo)

        from_to = from_data['to'].get(to_oid)
        if from_to is None:
            from_to = from_data['to'][to_oid] = []
        from_to.append(ref)

        to_data = result.get(to_oid)
        if to_data is None:
            to_data = result[to_oid] = {
                'to': {}, 'from': {}, 'serials': [],
                }
        to_from = to_data['from'].get(from_oid)
        if to_from is None:
            to_from = to_data['from'][from_oid] = []
        to_from.append(ref)

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
