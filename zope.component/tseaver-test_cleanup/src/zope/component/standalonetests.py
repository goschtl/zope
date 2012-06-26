"""
See: https://bugs.launchpad.net/zope3/+bug/98401
"""
import unittest
import doctest
import sys
import pickle

if __name__ == "__main__": #pragma NO COVER (runs in subprocess)
    sys.path = pickle.loads(sys.stdin.read())

    from zope.interface import Interface
    from zope.interface import implementer

    with open('/tmp/foo.txt', 'w') as f:
        print >>f, sys.executable
        print >>f, '-' * 80
        for p in sys.path:
            print >>f, p
        print >>f, '-' * 80
        import zope
        for p in zope.__path__:
            print >>f, p

    class I1(Interface):
        pass

    class I2(Interface):
        pass

    @implementer(I1)
    class Ob(object):
        def __repr__(self):
            return '<instance Ob>'

    ob = Ob()

    @implementer(I2)
    class Comp(object):
        def __init__(self, context):
            self.context = context

    import zope.component
    zope.component.provideAdapter(Comp, (I1,), I2)
    adapter = I2(ob)
    assert adapter.__class__ is Comp
    assert adapter.context is ob
