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
from cStringIO import StringIO
from cPickle import Unpickler, Pickler
import sys

from ZODB.POSException import ConflictError

#import traceback

bad_classes = {}

def bad_class(class_tuple):
    if bad_classes.has_key(class_tuple) or class_tuple[0][0] == '*':
        # if we've seen the class before or if it's a ZClass, we know that
        # we can't resolve the conflict
        return 1

ResolvedSerial = 'rs'

def _classFactory(location, name,
                  _silly=('__doc__',), _globals={}):
    return getattr(__import__(location, _globals, _globals, _silly),
                   name)

def state(self, oid, serial, prfactory, p=''):
    p = p or self.loadSerial(oid, serial)
    file = StringIO(p)
    unpickler = Unpickler(file)
    unpickler.persistent_load = prfactory.persistent_load
    class_tuple = unpickler.load()
    state = unpickler.load()
    return state


class PersistentReference:

    def __repr__(self):
        return "PR(%s %s)" % (id(self), self.data)

    def __getstate__(self):
        raise "Can't pickle PersistentReference"

class PersistentReferenceFactory:

    data = None

    def persistent_load(self, oid):
        if self.data is None:
            self.data = {}

        r = self.data.get(oid, None)
        if r is None:
            r = PersistentReference()
            r.data = oid
            self.data[oid] = r

        return r

def persistent_id(object):
    if getattr(object, '__class__', 0) is not PersistentReference:
        return None
    return object.data

def tryToResolveConflict(self, oid, committedSerial, oldSerial, newpickle,
                         committedData=''):
    #class_tuple, old, committed, newstate = ('',''), 0, 0, 0
    try:
        file = StringIO(newpickle)
        unpickler = Unpickler(file)
        prfactory = PersistentReferenceFactory()
        unpickler.persistent_load = prfactory.persistent_load
        class_tuple = unpickler.load()[0]
        if bad_class(class_tuple):
            return 0

        newstate = unpickler.load()
        klass = _classFactory(class_tuple[0], class_tuple[1])
        inst = klass.__basicnew__()

        try:
            resolve = inst._p_resolveConflict
        except AttributeError:
            bad_classes[class_tuple] = 1
            return 0

        old = state(self, oid, oldSerial, prfactory)
        committed = state(self, oid, committedSerial, prfactory, committedData)

        resolved = resolve(old, committed, newstate)

        file = StringIO()
        pickler = Pickler(file,1)
        pickler.persistent_id = persistent_id
        pickler.dump(class_tuple)
        pickler.dump(resolved)
        return file.getvalue(1)
    except ConflictError:
        return 0

class ConflictResolvingStorage:
    "Mix-in class that provides conflict resolution handling for storages"

    tryToResolveConflict = tryToResolveConflict
