from zope import interface, component
from zope.interface import declarations

class Implements(declarations.Implements):
    """A pickleable implements declaration"""

    def __reduce__(self):
        return Implements, self.__bases__

class ImplementsDescriptor(object):

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('__implemented__')

        if '__implemented__' not in instance.__dict__:
            instance.__implemented__ = interface.implementedBy(
                instance.__call__)
        return instance.__dict__['__implemented__']
    
    def __set__(self, instance, value):
        instance.__dict__['__implemented__'] = Implements(*value)

    def __delete__(self, instance):
        if '__implemented__' not in instance.__dict__:
            raise AttributeError('__implemented__')
        del instance.__dict__['__implemented__']

class AdaptsDescriptor(object):

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('__implemented__')

        return component.adaptedBy(instance.__call__)

class Declarer(object):

    __implemented__ = ImplementsDescriptor()
    __component_adapts__ = AdaptsDescriptor()
