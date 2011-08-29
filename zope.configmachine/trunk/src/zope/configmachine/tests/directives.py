from zope.interface import Interface
from zope.interface import Attribute

class F(object):
    def __repr__(self):
        return 'f'
    def __call__(self, *a, **k):
        pass

f = F()

class ISimple(Interface):
    a = Attribute('a')
    b = Attribute('b')
    c = Attribute('c')

def simple(context, a=None, c=None, b=u"xxx"):
    return [(('simple', a, b, c), f, (a, b, c))]

