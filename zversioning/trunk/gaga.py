#! /usr/local/env/python
from cStringIO import StringIO
import cPickle
from cPickle import Pickler, Unpickler, loads
  
from persistent import Persistent
  
def isVersionable(obj) :
    return getattr(obj, "__versionable__", False)
   
class AtomicPickler(object) :

    def __init__(self, repository) :
        stream = self.stream = StringIO()
        self.repository = repository
        self.pickler = Pickler(stream, 1)
        self.pickler.persistent_id = self.persistent_id
        self.init = True
       
    def persistent_id(self, obj) :
        if self.init :
            return None
        if self.isVersionable(obj) :
            return self.repository.getReferenceId(obj)
        return obj
         
    def dump(self, obj) :
        self.init = True
        self.stream.seek(0)
        self.pickler.dump(obj)
        return self.stream.getvalue()      
        
class AtomicUnpickler(object) :

    def __init__(self, repository) :
        stream = self.stream = StringIO()
        self.repository = repository
        self.pickler = Pickler(stream, 1)
        self.pickler.persistent_id = self.persistent_id
        self.init = True
       
    def persistent_id(self, obj) :
        if self.init :
            return None
        if self.isVersionable(obj) :
            return self.repository.getReferenceId(obj)
        return obj
         
    def dump(self, obj) :
        self.init = True
        self.stream.seek(0)
        self.pickler.dump(obj)
        return self.stream.getvalue()      

            
   
class Repository(object) :
    """ A simple dict simulation of an arbitrary data store. """
    
    counter = 0
    storage = {}
    
    def __init__(self) :
        self.atomic_pickler = AtomicPickler(self)
    
    def getTicket(self, obj) :
        if hasattr(obj, "__ticket__") :
            return obj.__ticket__
        self.counter += 1
        return self.counter
        
    def getReferenceId(self, ticket) :
        return "guid of %s" % ticket
  
    def store(self, ticket, obj) :
        self.storage[ticket] = self.atomic_pickler.dump(obj)
        
    def load(self, ticket) :
        return cPickle.loads(self.storage[ticket])
        
        
    
class ReferencePickler :
    """ Help class to store wrapped references. """
    
    def __init__(self, repository) :
        self.repository = repository
        self.counter = 0
             
              
    def writeReference(self, obj):
        print "writeReference", obj
        self.counter += 1
        if self.counter == 1 :
            return None
        
        if isVersionable(obj) : 
            print "isVersionable", obj
            ticket = self.repository.getTicket(obj)
            self.repository.store(ticket, obj)
            return None
            key = repository.getReferenceId(ticket)
            print "   new version", key
            return key
            
        return obj
        
    def readReference(self, obj) :
        if isinstance(obj, str) and obj.startswith("our id") :
            return self.ids[obj]
        return obj
                 

class Dummy(object) :
    
    __versionable__ = True
    
    def __getstate__(self):
        print "pickling:", self.__dict__
        return self.__dict__
        
    def __setstate__(self, state) :
        print "unpickling:", state
        self.__dict__ = state
    
  
 
repository = Repository()

class InnerDummy(Dummy) : pass
class InnerInnerDummy(Dummy) : pass  


innerdummy = InnerDummy()
innerinnderdummy = InnerInnerDummy()
innerdummy.level2 = innerinnderdummy
 
dummy = Dummy()
dummy.__anno__ = {'component1': 'blah', 'component2': 'trallalla'}
dummy.simple = 3
dummy.subdummy = innerdummy

stream = StringIO()
p = Pickler(stream, 1)
helper = ReferencePickler(repository)
p.persistent_id = helper.writeReference
p.dump(dummy)


print "Repository"
for key, value in repository.storage.items() :
    print key
    print value
    print key, ":", len(value), "bytes", repository.load(key)
    
#print "gepoeckelt", stream.getvalue()




# stream.seek(0)
# u = Unpickler(stream)
# u.persistent_load = helper.sniffed
# u.noload()
# 
# print "sniffed", helper.sniffed
# 



