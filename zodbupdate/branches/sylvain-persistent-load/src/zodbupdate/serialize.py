##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from ZODB.broken import find_global
import cPickle
import cStringIO


class ZODBReference:
    """Class to remenber reference we don't want to touch.
    """

    def __init__(self, ref):
        self.ref = ref


class ObjectRenamer:
    """This load and save a ZODB record, modifying all references to
    renamed class according the given renaming rules:

    - in global symbols contained in the record,

    - in persistent reference information,

    - in class information (first pickle of the record).
    """

    def __init__(self, changes):
        self.__changes = dict()
        for old, new in changes.iteritems():
            self.__changes[tuple(old.split(' '))] = tuple(new.split(' '))
        self.__changed = False

    def __find_global(self, *names):
        """Find a class with the given name, looking for a renaming
        rule first.

        Using ZODB find_global let us manage missing classes.
        """
        if names in self.__changes:
            names = self.__changes[names]
            self.__changed = True
        return find_global(*names)

    def __persistent_load(self, reference):
        """Load a persistent reference. The reference might changed
        according a renaming rules. We give back a special object to
        represent that reference, and not the real object designated
        by the reference.
        """
        if isinstance(reference, tuple):
            oid, klass = reference
            if klass in self.__changes:
                klass = self.__changes[klass]
                self.__changed = True
            return ZODBReference((oid, klass))
        # TODO multidatabase ['m'], (database, oid, klass)
        return ZODBReference(reference)

    def __unpickler(self, pickle):
        """Create an unpickler with our custom global symbol loader
        and reference resolver.
        """
        unpickler = cPickle.Unpickler(pickle)
        unpickler.persistent_load = self.__persistent_load
        unpickler.find_global = self.__find_global
        return unpickler

    def __persistent_id(self, obj):
        """Save the given object as a reference only if it was a
        reference before. We re-use the same information.
        """
        if not isinstance(obj, ZODBReference):
            return None
        return obj.ref

    def __pickler(self, output):
        """Create a pickler able to save to the given file, objects we
        loaded while paying attention to any reference we loaded.
        """
        pickler = cPickle.Pickler(output, 1)
        pickler.persistent_id = self.__persistent_id
        return pickler

    def __update_class_meta(self, class_meta):
        """Update class information, which can contain information
        about a renamed class.
        """
        if isinstance(class_meta, tuple):
            klass, args = class_meta
            if isinstance(klass, tuple):
                if klass in self.__changes:
                    self.__changed = True
                    return self.__changes[klass], args
        return class_meta

    def rename(self, input_file):
        """Take a ZODB record (as a file object) as input. We load it,
        replace any reference to renamed class we know of. If any
        modification are done, we save the record again and return it,
        return None otherwise.
        """
        self.__changed = False

        unpickler = self.__unpickler(input_file)
        class_meta = unpickler.load()
        data = unpickler.load()

        class_meta = self.__update_class_meta(class_meta)

        if not self.__changed:
            return None

        output_file = cStringIO.StringIO()
        pickler = self.__pickler(output_file)
        pickler.dump(class_meta)
        pickler.dump(data)

        output_file.truncate()
        return output_file
