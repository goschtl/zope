from cStringIO import StringIO
from cPickle import Pickler, Unpickler

ids = {}

def persistent_id(ob):
    myid = id(ob)
    ids[myid] = ob
    return myid

class Dummy:
    def __getstate__(self):
        print self.__dict__
        return self.__dict__
    
dummy = Dummy()
dummy.__anno__ = {'component1': 'blah', 'component2': 'trallalla'}
dummy.simple = 3

stream = StringIO()
p = Pickler(stream, 1)
p.persistent_id = persistent_id
p.dump(dummy)
print stream

"""
stream.seek(0)
u = Unpickler(stream)
u.persistent_load = ids.get
u.load()
"""