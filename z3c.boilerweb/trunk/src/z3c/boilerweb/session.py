from zope.session.interfaces import ISession

class SessionProperty(object):
    def __init__(self, name, default=None, key=None, keyFunc=None):
        self.name = name
        self.default = default
        self.key = key
        self.keyFunc = keyFunc
        if key and keyFunc:
            raise TypeError("Can't specify both key and keyFunc")

    def __get__(self, inst, klass):
        if self.key:
            key = self.key
        elif self.keyFunc:
            key = self.keyFunc(inst)
        else:
            key = '%s.%s' % (klass.__module__, klass.__name__)
        session = ISession(inst.request)[key]
        return session.get(self.name, self.default)

    def __set__(self, inst, value):
        if self.key:
            key = self.key
        elif self.keyFunc:
            key = self.keyFunc(inst)
        else:
            klass = inst.__class__
            key = '%s.%s' % (klass.__module__, klass.__name__)
        session = ISession(inst.request)[key]
        session[self.name] = value
