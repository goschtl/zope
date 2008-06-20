from zope.security.checker import NamesChecker

from sqlalchemy import orm

import interfaces
import relations
import soup

class Tuple(object):
    def __init__(self):
        self.data = []

    @property
    def adapter(self):
        return self._sa_adapter

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
            relation = relations.Relation()
            relation.target = item
            relation.order = len(converted)

            converted.append(relation)
            
        return converted

    def __iter__(self):
        for relation in iter(self.data):
            obj = relation.target
            if interfaces.IBasicType.providedBy(obj):
                yield obj.value
            else:
                yield obj
                
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return repr(tuple(self))
    
class OrderedList(Tuple):
    __Security_checker__ = NamesChecker(
        ('append', 'remove'))

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
        relation = relations.Relation()
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

    def __repr__(self):
        return repr(list(self))
    
    def __getitem__(self, index):
        return self.data[index].target
        
    def __setitem__(self, index, value):
        return NotImplementedError("Setting items at an index is not implemented.")

