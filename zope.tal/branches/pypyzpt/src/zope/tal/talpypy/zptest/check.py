import sys

if len(sys.argv) == 2 and sys.argv[1] == 'so':
    print 'so extension'
    import zptest
else:    
    from pypy.interpreter.mixedmodule import testmodule
    zptest =  testmodule('zptest', 'zope.tal.pypy')

ip = zptest.Interpreter(None, 20)
assert ip.power2() == 400
assert ip.getInstance() is None

ip = zptest.Interpreter([1, 2], 10)
assert ip.power2() == 100
assert ip.getInstance() == [1, 2, 3]

print "tests passed"
