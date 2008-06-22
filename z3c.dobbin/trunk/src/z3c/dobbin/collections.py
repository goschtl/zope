from zope.security.checker import NamesChecker

from sqlalchemy import orm

import interfaces
import relations
import soup
import types

class Tuple(object):
    def __init__(self):
        self.data = []

    @property
    def adapter(self):
        return orm.collections.collection_adapter(self)

    @orm.collections.collection.appender
    def _appender(self, item):
        self.data.append(item)
    
    @orm.collections.collection.iterator
    def _iterator(self):
        return iter(self.data)

    @orm.collections.collection.remover
    def _remover(self, item):
        self.data.remove(item)

    @orm.collections.collection.converter
    def convert(self, items):
        converted = []
        
        for item in items:
            if not interfaces.IMapped.providedBy(item):
                item = soup.persist(item)

            # set up relation
            relation = relations.OrderedRelation()
            relation.target = item
            relation.order = len(converted)

            converted.append(relation)
            
        return converted

    def __iter__(self):
        return (self[i] for i in range(len(self.data)))
                
    def __getitem__(self, index):
        obj = self.data[index].target
        if interfaces.IBasicType.providedBy(obj):
            return obj.value
        else:
            return obj
                        
    def __setitem__(self, index, value):
        return TypeError("Object does not support item assignment.")

    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return repr(tuple(self))
    
class OrderedList(Tuple):
    __Security_checker__ = NamesChecker(
        ('append', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort'))

    @orm.collections.collection.appender
    def _appender(self, item):
        self.data.append(item)
    
    @orm.collections.collection.iterator
    def _iterator(self):
        return iter(self.data)

    @orm.collections.collection.remover
    def _remover(self, item):
        self.data.remove(item)

    @orm.collections.collection.internally_instrumented
    def append(self, item, _sa_initiator=None):
        if not interfaces.IMapped.providedBy(item):
            item = soup.persist(item)

        # set up relation
        relation = relations.OrderedRelation()
        relation.target = item
        relation.order = len(self.data)

        self.adapter.fire_append_event(relation, _sa_initiator)
        
        # add relation to internal list
        self.data.append(relation)

    @orm.collections.collection.internally_instrumented
    def remove(self, item, _sa_initiator=None):
        if interfaces.IMapped.providedBy(item):
            uuid = item.uuid
        else:
            uuid = item._d_uuid

        for relation in self.data:
            if relation.right == uuid:
                self.adapter.fire_remove_event(relation, _sa_initiator)
                self.data.remove(relation)
                break
        else:
            raise ValueError("Not in list: %s" % item)
        
    def extend(self, items):
        map(self.append, items)

    def count(self, value):
        return list(self).count(value)

    def index(self, value, **kwargs):
        for index in range(len(self)):
            if self[index] == value:
                return index

        raise ValueError("%s not found in list." % value)

    @orm.collections.collection.internally_instrumented
    def insert(self, index, item):
        stack = self.data[index:]
        del self.data[index:]
        self.append(item)
        for relation in stack:
            relation.order += 1
            self.data.append(relation)

    @orm.collections.collection.internally_instrumented
    def pop(self, index=-1, _sa_initiator=None):
        relation = self.data[index]
        obj = relation.target
        
        self.adapter.fire_remove_event(relation, _sa_initiator)
        del self.data[index]
        
        stack = self.data[index:]
        for relation in stack:
            relation.order -= 1

        return obj
    
    def reverse(self):
        self.data.reverse()
        for index in range(len(self.data)):
            self.data[index].order = index
        
    def sort(self, **kwargs):
        data = list(self)
        data_relation_mapping = zip(data, self.data)

        mapping = {}
        for item, relation in data_relation_mapping:
            relations = mapping.setdefault(item, [])
            relations.append(relation)

        data.sort(**kwargs)
        del self.data[:]
        
        for item in data:
            relation = mapping[item].pop()
            relation.order = len(self.data)
            self.data.append(relation)            
                
    def __repr__(self):
        return repr(list(self))

    @orm.collections.collection.internally_instrumented
    def __setitem__(self, index, value, _sa_initiator=None):
        # remove previous
        relation = self.data[index]
        self.adapter.fire_remove_event(relation, _sa_initiator)

        # add new
        self.append(value)
        relation = self.data[-1]
        del self.data[-1]

        # replace previous
        relation.order = index
        self.data[index] = relation

class Dict(dict):
    __Security_checker__ = NamesChecker(
        ('clear', 'copy', 'fromkeys', 'get', 'has_key', 'items', 'iteritems', 'iterkeys', 'itervalues', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'))

    @property
    def adapter(self):
        return orm.collections.collection_adapter(self)

    @orm.collections.collection.appender
    @orm.collections.collection.replaces(1)    
    def _appender(self, item):
        dict.__setitem__(self, item.key, item)
    
    @orm.collections.collection.iterator
    def _iterator(self):
        return dict.itervalues(self)

    @orm.collections.collection.remover
    def _remover(self, item):
        dict.remove(item)

    @orm.collections.collection.internally_instrumented
    def __setitem__(self, key, item, _sa_initiator=None):
        if not interfaces.IMapped.providedBy(item):
            item = soup.persist(item)

        # mapped objects may be used as key; internally, we'll use
        # the UUID in this case, however.
        if interfaces.IMapped.providedBy(key):
            key = key.uuid

        assert isinstance(key, types.StringTypes), \
               "Only strings or mapped objects may be used as keys."
            
        # set up relation
        relation = relations.KeyRelation()
        relation.target = item
        relation.key = key

        self.adapter.fire_append_event(relation, _sa_initiator)
        dict.__setitem__(self, key, relation)

    @orm.collections.collection.converter
    def convert(self, d):
        converted = []
        
        for key, item in d.items():
            if not interfaces.IMapped.providedBy(item):
                item = soup.persist(item)

            # set up relation
            relation = relations.KeyRelation()
            relation.target = item
            relation.key = key

            converted.append(relation)
            
        return converted

    def values(self):
        return [self[key] for key in self]

    def itervalues(self):
        return (self[key] for key in self)

    @orm.collections.collection.internally_instrumented
    def pop(self, key, _sa_initiator=None):
        relation = dict.pop(self, key)
        obj = relation.target
        
        self.adapter.fire_remove_event(relation, _sa_initiator)

        if interfaces.IBasicType.providedBy(obj):
            return obj.value
        else:
            return obj

    @orm.collections.collection.internally_instrumented
    def popitem(self, _sa_initiator=None):
        key, relation = dict.popitem(self)
        obj = relation.target

        self.adapter.fire_remove_event(relation, _sa_initiator)

        if interfaces.IBasicType.providedBy(obj):
            return key, obj.value
        else:
            return key, obj

    @orm.collections.collection.internally_instrumented
    def clear(self, _sa_initiator=None):
        for relation in dict.itervalues(self):
            self.adapter.fire_remove_event(relation, _sa_initiator)            

        dict.clear(self)
        
    def __getitem__(self, key):
        # mapped objects may be used as key; internally, we'll use
        # the UUID in this case, however.
        if interfaces.IMapped.providedBy(key):
            key = key.uuid

        assert isinstance(key, types.StringTypes), \
               "Only strings or mapped objects may be used as keys."

        obj = dict.__getitem__(self, key).target
        if interfaces.IBasicType.providedBy(obj):
            return obj.value
        else:
            return obj

    def __repr__(self):
        return repr(dict(
            (key, self[key]) for key in self))
