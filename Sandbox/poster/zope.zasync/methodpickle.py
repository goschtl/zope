import types
import copy_reg
import cPickle

def unpickleInstanceMethod(instance, methodname):
    i = cPickle.loads(instance)
    res = getattr(i, methodname, None)
    assert isinstance(res, types.MethodType)
    return res

def pickleInstanceMethod(ob):
    return (
        unpickleInstanceMethod,
        (cPickle.dumps(ob.im_self, 2), ob.__name__))

def register():
    copy_reg.pickle(types.MethodType, pickleInstanceMethod)
