from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.proxy import removeAllProxies
from zope.interface import implements
from zope.app import zapi

from persistent.dict import PersistentDict
from persistent import Persistent

from interfaces import IOptionStorage, IOptionDict

from UserDict import IterableUserDict

OptionStorageKey = "optionstorage"

class Table(object):
    # Based on zope's SecurityMap.

    def __init__(self):
        self._byrow = {}
        self._bycol = {}

    def __nonzero__(self):
        return bool(self._byrow)

    def _changed(self):
        pass

    def clear(self):
        self._byrow.clear()
        self._bycol.clear()
        self._changed()

    def addCell(self, rowkey, colkey, value):
        row = self._byrow.get(rowkey)
        if row:
            if row.get(colkey) is value:
                return False
        else:
            row = self._byrow[rowkey] = {}

        col = self._bycol.get(colkey)
        if not col:
            col = self._bycol[colkey] = {}
            
        row[colkey] = value
        col[rowkey] = value
        
        self._changed()

        return True

    def delCell(self, rowkey, colkey):
        row = self._byrow.get(rowkey)
        if row and (colkey in row):
            del row[colkey]
            if not row:
                del self._byrow[rowkey]
            col = self._bycol[colkey]
            del col[rowkey]
            if not col:
                del self._bycol[colkey]
            return True

        self._changed()

        return False

    def queryCell(self, rowkey, colkey, default=None):
        row = self._byrow.get(rowkey)
        if row:
            return row.get(colkey, default)
        else:
            return default

    def getCell(self, rowkey, colkey):
        marker = object()
        cell = self.queryCell(rowkey, colkey, marker)
        if cell is marker:
            raise KeyError, "Invalid row/column pair"
        return cell

    def getRow(self, rowkey):
        row = self._byrow.get(rowkey)
        if row:
            return row.items()
        else:
            return []

    def getCol(self, colkey):
        col = self._bycol.get(colkey)
        if col:
            return col.items()
        else:
            return []

    def getRowKeys(self):
        return self._byrow.keys()

    def getColKeys(self):
        return self._bycol.keys()

    def getAllCells(self):
        res = []
        for r in self._byrow.keys():
            for c in self._byrow[r].items():
                res.append((r,) + c)
        return res


class PersistentTable(Table, Persistent):

    def _changed(self):
        self._p_changed = 1


class OptionDict(Persistent):

    implements(IOptionDict)

    def __init__(self):
        self._defaultkey = None
        self._defaultlanguage = None
        self._table = PersistentTable()

    def getLanguages(self):
        return self._table.getColKeys()

    def getDefaultLanguage(self):
        return self._defaultlanguage

    def setDefaultLanguage(self, language):
        self._defaultlanguage = language

    def getDefaultKey(self):
        return self._defaultkey

    def setDefaultKey(self, key):
        self._defaultkey = key

    def getKeys(self):
        return self._table.getRowKeys()

    def queryValue(self, key, language, default=None):
        return self._table.queryCell(key, language, default)

    def getValue(self, key, language):
        return self._table.getCell(key, language)

    def addValue(self, key, language, value):
        self._table.addCell(key, language, value)

    def delValue(self, key, language):
        self._table.delCell(key, language)

    def delAllValues(self):
        self._table.clear()
        self._defaultkey = None


class OptionStorage(IterableUserDict, object):

    implements(IOptionStorage)

    def __init__(self, context):
        annotations = IAnnotations(removeAllProxies(context))
        if OptionStorageKey in annotations:
            self.data = annotations[OptionStorageKey]
        else:
            self.data = annotations[OptionStorageKey] = PersistentDict()

def queryOptionStorage(context, name):
    lookuplist = zapi.getParents(context)
    lookuplist.insert(0, context)
    for object in lookuplist:
        object = removeAllProxies(object)
        if IAnnotatable.providedBy(object):
            annotations = IAnnotations(object)
            if OptionStorageKey in annotations:
                storage = IOptionStorage(object)
                if name in storage:
                    return storage[name]
    return None

class OptionStorageProperty(object):
    
    def __init__(self, name, dictname, islist=False, readonly=False):
        self._name = name
        self._dictname = dictname
        self._islist = islist
        self._readonly = readonly

    def __get__(self, object, type_=None):
        dict = queryOptionStorage(object, self._dictname)
        if dict:
            default = dict.getDefaultKey()
        return getattr(object, self._name, default)

    def __set__(self, object, value):
        if self._readonly:
            raise AttributeError, "Attribute '%s' is read-only" % self._name
        if type(value) is not list:
            values = [value]
        else:
            values = value
        dict = queryOptionStorage(object, self._dictname)
        if dict:
            keys = dict.getKeys()
            invalid = [x for x in values if x not in keys]
            if invalid:
                raise ValueError, "Invalid values: %s" % \
                                  ", ".join(map(repr, invalid))
        if self._islist:
            value = values
        setattr(object, self._name, value)

