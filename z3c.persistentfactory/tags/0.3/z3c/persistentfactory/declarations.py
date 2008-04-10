from zope import interface, component
from zope.interface import declarations

class Implements(declarations.Implements):
    """A pickleable implements declaration"""

    def __reduce__(self):
        return Implements, self.__bases__

class ImplementsDescriptor(declarations.Implements):

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if '__implemented__' not in instance.__dict__:
            raise AttributeError('__implemented__')

        return instance.__dict__['__implemented__']
    
    def __set__(self, instance, value):
        if not isinstance(value, Implements):
            value = Implements(*value)

        instance.__dict__['__implemented__'] = value

    def __delete__(self, instance):
        if '__implemented__' not in instance.__dict__:
            raise AttributeError('__implemented__')

        del instance.__dict__['__implemented__']

class Declarer(object):

    def __init__(self, *args, **kw):
        self.__implemented__ = interface.implementedBy(
            self.__call__.im_func)
        self.__component_adapts__ = component.adaptedBy(
            self.__call__.im_func)
        super(Declarer, self).__init__(*args, **kw)

    def __call__(self):
        return self

implemented = interface.implementedBy(Declarer)
Declarer.__implemented__ = ImplementsDescriptor(*implemented)
