import copy
import inspect


def delegate(name):
    def inner(self, *args, **kw):
        return getattr(self.stack[-1], name)(*args, **kw)
    return inner


def stackable(original):
    type_ = type(original)

    class inner(object):

        for name in dict(
            inspect.getmembers(type_, predicate=inspect.ismethoddescriptor)):
            if name in ['__getattribute__', '__setattr__']:
                continue
            locals()[name] = delegate(name)

        def __init__(self, original):
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

    stack = inner(original)
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
