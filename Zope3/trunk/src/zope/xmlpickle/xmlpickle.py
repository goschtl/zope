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
"""Pickle-based serialization of Python objects to and from XML.

$Id: xmlpickle.py,v 1.3 2003/05/01 11:00:05 jim Exp $
"""

from xml.parsers import expat
from cStringIO import StringIO
from cPickle import loads as _standard_pickle_loads
from pickle import \
     Pickler as _StandardPickler, \
     MARK as _MARK, \
     EMPTY_DICT as _EMPTY_DICT, \
     DICT as _DICT, \
     SETITEM as _SETITEM, \
     SETITEMS as _SETITEMS

from zope.xmlpickle import ppml

class _PicklerThatSortsDictItems(_StandardPickler):
    dispatch = {}
    dispatch.update(_StandardPickler.dispatch)

    def save_dict(self, object):
        d = id(object)

        write = self.write
        save  = self.save
        memo  = self.memo

        if self.bin:
            write(_EMPTY_DICT)
        else:
            write(_MARK + _DICT)

        memo_len = len(memo)
        self.write(self.put(memo_len))
        memo[d] = (memo_len, object)

        using_setitems = (self.bin and (len(object) > 1))

        if using_setitems:
            write(_MARK)

        items = object.items()
        items.sort()
        for key, value in items:
            save(key)
            save(value)

            if not using_setitems:
                write(_SETITEM)

        if using_setitems:
            write(_SETITEMS)

    dispatch[dict] = save_dict

def _dumpsUsing_PicklerThatSortsDictItems(object, bin = 0):
    file = StringIO()
    _PicklerThatSortsDictItems(file, bin).dump(object)
    return file.getvalue()

def p2xml(p):
    """Convert a standard Python pickle to xml
    """
    u = ppml.ToXMLUnpickler(StringIO(p))
    xmlob = u.load()
    r = ['<?xml version="1.0" encoding="utf-8" ?>\n']
    xmlob.output(r.append)
    return ''.join(r)
    
def dumps(ob):
    """Serialize an object to XML
    """
    p = _dumpsUsing_PicklerThatSortsDictItems(ob, 1)
    return p2xml(p)

def xml2p(xml):
    """Convert xml to a standard Python pickle
    """
    handler = ppml.xmlPickler()
    parser = expat.ParserCreate()
    parser.CharacterDataHandler = handler.handle_data
    parser.StartElementHandler = handler.handle_starttag
    parser.EndElementHandler = handler.handle_endtag
    parser.Parse(xml)
    pickle = handler.get_value()
    pickle = str(pickle)
    return pickle

def loads(xml):
    """Create an object from serialized XML
    """
    pickle = xml2p(xml)
    ob = _standard_pickle_loads(pickle)
    return ob
