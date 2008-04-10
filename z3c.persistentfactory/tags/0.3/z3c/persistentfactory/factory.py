import new

from zope import interface, component
import persistent
            
import declarations

class PersistentFactory(declarations.Declarer, persistent.Persistent):

    def __init__(self, method):
        self.context = method.im_self
        self.__name__ = method.__name__
        super(PersistentFactory, self).__init__()

    @property
    def __call__(self):
        type_ = type(self.context)
        return new.instancemethod(
            getattr(type_, self.__name__), self.context, type_)

class Factory(object):

    def __init__(self, callable_):
        self.callable = callable_

    def __get__(self, instance, owner):
        method = new.instancemethod(self.callable, instance, owner)
        if instance is None:
            # when accessed for the class, just return the method
            return method

        result = PersistentFactory(method)
        setattr(instance, method.__name__, result)
        return result

factory = Factory
