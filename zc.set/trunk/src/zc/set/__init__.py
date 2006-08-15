import persistent

def simpleWrapper(name):
    def wrapper(self, *args, **kwargs):
        return getattr(self._data, name)(*args, **kwargs)
    return wrapper

def mutatingWrapper(name):
    def wrapper(self, *args, **kwargs):
        res = getattr(self._data, name)(*args, **kwargs)
        self._p_changed = True
        return res
    return wrapper

def mutatingStrippingWrapper(name):
    def wrapper(self, other):
        if isinstance(other, self.__class__):
            other = other._data
        getattr(self._data, name)(other)
        self._p_changed = True
        return self # this is used necessary for all the __i*__, so we have to
        # return the mutated value
    return wrapper

def persistentOutputWrapper(name):
    def wrapper(self, *args, **kwargs):
        res = getattr(self._data, name)(*args, **kwargs)
        inst = self.__class__()
        inst._data = res
        return inst
    return wrapper

def persistentOutputStrippingWrapper(name):
    def wrapper(self, other):
        if isinstance(other, self.__class__):
            other = other._data
        res = getattr(self._data, name)(other)
        inst = self.__class__()
        inst._data = res
        return inst
    return wrapper

def strippingWrapper(name):
    def wrapper(self, other):
        if isinstance(other, self.__class__):
            other = other._data
        return getattr(self._data, name)(other)
    return wrapper


class Set(persistent.Persistent):
    def __init__(self, iterable=()):
        self._data = set(iterable)

    for nm in ('__cmp__', '__contains__', '__hash__', '__iter__', '__len__'):
        locals()[nm] = simpleWrapper(nm)

    for nm in ('__eq__', '__ge__', '__gt__', '__le__', '__lt__', '__ne__',
               'issubset', 'issuperset'):
        locals()[nm] = strippingWrapper(nm)

    for nm in ('difference', 'intersection', 'symmetric_difference', 'union'):
        locals()[nm] = persistentOutputWrapper(nm)

    for nm in ('__and__', '__or__', '__rand__', '__ror__', '__rsub__',
               '__rxor__', '__sub__', '__xor__'):
        locals()[nm] = persistentOutputStrippingWrapper(nm)

    for nm in ('add', 'clear', 'difference_update', 'discard',
               'intersection_update', 'pop', 'remove',
               'symmetric_difference_update', 'update'):
        locals()[nm] = mutatingWrapper(nm)

    for nm in ('__iand__', '__ior__', '__isub__', '__ixor__'):
        locals()[nm] = mutatingStrippingWrapper(nm)

    def copy(self):
        return self.__class__(self._data)

    def __repr__(self):
        return '%s.%s%s' % (
            self.__class__.__module__,
            self.__class__.__name__,
            repr(self._data)[3:])
