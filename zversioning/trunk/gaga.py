#! /usr/local/env/python
from cStringIO import StringIO
import cPickle
from cPickle import Pickler, Unpickler, loads

from persistent import Persistent

def isVersionable(obj) :
    return getattr(obj, "__versionable__", False)

class AtomicPickler(object) :
    """Repository frontend searching the 'atoms' borders :-).
    
    This class actually missuses the pickle functionality to
    follow every reference originating from the given object.
    """

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
        self.unpickler = Unpickler(stream)
        self.unpickler.persistent_load = self.persistent_load
       
    def persistent_load(self, string) :
        if repository.isReferenceId(string):
            # the string is a refId
            return repository.getObject(string)
            
    def loads(self, string) :
        self.stream.seek(0)
        return self.unpickler.load()

class Repository(object) :
    """ A simple dict simulation of an arbitrary data store. 
    
    Manages also generating unique tickets."""
    
    counter = 0
    storage = {}
    
    def __init__(self) :
        self.atomic_pickler = AtomicPickler(self)
        self.atomic_unpickler = AtomicUnpickler(self)
    
    def getTicket(self, obj) :
        if hasattr(obj, "__ticket__") :
            return obj.__ticket__
        self.counter += 1
        return self.counter
        
    def getReferenceId(self, ticket) :
        return "GUID:%s" % ticket
  
    def isReferenceId(self, refId):
        return isinstance(refId, str) and refId.startswith("GUID:")
    
    def getObject(self, refId):
        self.load(refId.split(':')[1])
    
    def store(self, ticket, obj) :
        self.storage[ticket] = self.atomic_pickler.dump(obj)
        
    def load(self, ticket) :
        return self.atomic_unpickler.loads(self.storage[ticket])
        
    
class ReferencePickler :
    """Helper class to store wrapped references. 
    """
    
    def __init__(self, repository) :
        self.repository = repository
        self.counter = 0
              
    def writeReference(self, obj):
        print "writeReference", obj
        self.counter += 1
        if self.counter == 1 :
            return None
        
        if isVersionable(obj) : 
            print "--> isVersionable\n"
            ticket = self.repository.getTicket(obj)
            self.repository.store(ticket, obj)
            return None
            
#        return obj      # ???
        
    def readReference(self, refId):
#        import pdb;pdb.set_trace()
        print "readReference", refId
        if self.repository.isReferenceId(refId):
            return self.repository.getObject(refId)

class Dummy(object) :
    
    __versionable__ = True
    
    def __getstate__(self):
        print "pickling:", self.__dict__
        return self.__dict__
        
    def __setstate__(self, state) :
        print "unpickling:", state
        self.__dict__ = state

class InnerDummy(Dummy) : pass
class InnerInnerDummy(Dummy) : pass  


repository = Repository()

dummy = Dummy()
innerdummy = InnerDummy()
innerinnderdummy = InnerInnerDummy()
 
dummy.__anno__ = {'component1': 'blah', 'component2': 'trallalla'}
dummy.simple = 3
dummy.subdummy = innerdummy
innerdummy.level2 = innerinnderdummy

helper = ReferencePickler(repository)

stream = StringIO()
p = Pickler(stream, 1)
p.persistent_id = helper.writeReference
p.dump(dummy)

print "------------------------"
if 0:
    print "Repository"
    for key, value in repository.storage.items() :
        print key
        print '   ', value
#        print key, ":", len(value), "bytes", repository.load(key)
    print "------------------------"

#print "gepoeckelt", stream.getvalue()


stream.seek(0)
u = Unpickler(stream)
u.persistent_load = helper.readReference
redummy = u.load()

print redummy

#import pdb; pdb.set_trace()

assert redummy.__anno__ == dummy.__anno__
assert redummy.simple == dummy.simple
assert redummy.subdummy.__class__ is dummy.subdummy.__class__
assert redummy.subdummy.level2.__class__ == dummy.subdummy.level2.__class__

print
