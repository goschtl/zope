
from ZODB.broken import find_global
import cPickle
import cStringIO


class ZODBReference:
    """Class to remenber reference we don't want to touch.
    """

    def __init__(self, ref):
        self.ref = ref


class ObjectRenamer:
    """This load and save a record using persistent_id and
    persistent_load methods defined in the ZODB code to change
    information at that point as well.
    """

    def __init__(self, changes):
        self.__changes = dict()
        for old, new in changes.iteritems():
            self.__changes[tuple(old.split(' '))] = tuple(new.split(' '))
        self.__changed = False

    def __find_global(self, *names):
        if names in self.__changes:
            names = self.__changes[names]
            self.__changed = True
        return find_global(*names)

    def __persistent_load(self, reference):
        if isinstance(reference, tuple):
            oid, klass = reference
            if klass in self.__changes:
                klass = self.__changes[klass]
                self.__changed = True
            return ZODBReference((oid, klass))
        # TODO multidatabase ['m'], (database, oid, klass)
        return ZODBReference(reference)

    def __unpickler(self, pickle):
        unpickler = cPickle.Unpickler(pickle)
        unpickler.persistent_load = self.__persistent_load
        unpickler.find_global = self.__find_global
        return unpickler

    def __persistent_id(self, obj):
        if not isinstance(obj, ZODBReference):
            return None
        return obj.ref

    def __pickler(self, output):
        pickler = cPickle.Pickler(output, 1)
        pickler.persistent_id = self.__persistent_id
        pickler.clear_memo()
        return pickler

    def __update_class_meta(self, class_meta):
        if isinstance(class_meta, tuple):
            klass, args = class_meta
            if isinstance(klass, tuple):
                if klass in self.__changes:
                    self.__changed = True
                    return self.__changes[klass], args
        return class_meta

    def rename(self, input_file):
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
