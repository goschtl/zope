import copy
import inspect


class StackableBase(object):

    def __init__(self, original=None):
        if original is not None:
            self.stack = [original]

    def push(self):
        self.stack.append(copy.copy(self.stack[-1]))

    def pop(self):
        self.stack.pop()

    def can_pop(self):
        return len(self.stack) > 1

    def reset(self):
        del self.stack[1:]

    def __repr__(self):
        return 'stackable:%r' % self.stack[-1]

    def __reduce_ex__(self, protocol):
        return (self.__class__, (), dict(stack=self.stack))

    @classmethod
    def delegate(cls, name):
        def inner(self, *args, **kw):
            return getattr(self.stack[-1], name)(*args, **kw)
        return inner

    @classmethod
    def create_for(cls, type_):
        exclude_methods = ['__getattribute__', '__setattr__']
        overridden_methods = dict(
            inspect.getmembers(cls, predicate=inspect.ismethod)).keys()
        exclude_methods.extend(overridden_methods)

        copied_methods = {}
        # XXX ismethoddescriptor is correct for type_ in [dict, list], but
        # probably not in general
        for name in dict(
            inspect.getmembers(type_, predicate=inspect.ismethoddescriptor)):
            if name in exclude_methods:
                continue
            copied_methods[name] = cls.delegate(name)

        return type(
            'Stackable%s' % type_.__name__.title(), (cls,), copied_methods)


SUPPORTED_TYPES = dict(
    (type_, StackableBase.create_for(type_)) for type_ in [dict, list])

for type_ in SUPPORTED_TYPES.values():
    locals()[type_.__name__] = type_


def stackable(original):
    type_ = type(original)

    try:
        factory = SUPPORTED_TYPES[type_]
    except KeyError:
        raise TypeError('%r is not stackable' % type_)

    stack = factory(original)
    REGISTRY.register(stack)
    return stack


class Registry(object):

    def __init__(self):
        self.listeners = []

    def register(self, obj):
        self.listeners.append(obj)

    def push(self):
        for obj in self.listeners:
            obj.push()

    def pop(self):
        for i, obj in reversed(list(enumerate(self.listeners))):
            if obj.can_pop():
                obj.pop()
            else:
                # obj was created on this "push level", which means its
                # lifetime is now over (since its parent container will pop)
                del self.listeners[i]

    def reset(self):
        for obj in self.listeners:
            obj.reset()

REGISTRY = Registry()


def push():
    REGISTRY.push()


def pop():
    REGISTRY.pop()


def reset():
    REGISTRY.reset()
