from zope import interface

from ore.alchemist import Session

import soup
import factory
import interfaces

class Relation(object):
    def _get_source(self):
        return soup.lookup(self.left)

    def _set_source(self, item):
        self.left = item.uuid

    def _get_target(self):
        return soup.lookup(self.right)

    def _set_target(self, item):
        if not interfaces.IMapped.providedBy(item):
            item = soup.persist(item)

        if item.id is None:
            session = Session()
            session.save(item)
                
        self.right = item.uuid

    source = property(_get_source, _set_source)
    target = property(_get_target, _set_target)

class OrderedRelation(Relation):
    pass

class KeyRelation(Relation):
    pass
    
class RelationProperty(property):
    
    def __init__(self, field):
        self.field = field
        self.name = field.__name__+'_relation'
        property.__init__(self, self.get, self.set)

    def get(kls, instance):
        item = getattr(instance, kls.name)
        obj = soup.lookup(item.uuid)

        if interfaces.IBasicType.providedBy(obj):
            return obj.value
        else:
            return obj

    def set(kls, instance, item):
        if not interfaces.IMapped.providedBy(item):
            item = soup.persist(item)
        
        if item.id is None:
            session = Session()
            session.save(item)

        setattr(instance, kls.name, item)
