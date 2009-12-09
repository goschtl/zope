import sys
import doctest
import unittest

def new_init(self, test, optionflags=0, setUp=None, tearDown=None,
             checker=None):
    unittest.TestCase.__init__(self)
    self._dt_optionflags = optionflags
    self._dt_checker = checker
    self._dt_test = test
    self._dt_setUp = setUp
    self._dt_tearDown = tearDown
    self._dt_globs = test.globs.copy()

def new_tearDown(self):
    test = self._dt_test

    if self._dt_tearDown is not None:
        self._dt_tearDown(test)

    test.globs.clear()
    test.globs.update(self._dt_globs)

doctest.DocTestCase.__init__ = new_init
doctest.DocTestCase.tearDown = new_tearDown

if sys.version_info < (3,):
    from StringIO import StringIO
    
    def new_write(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        StringIO.write(self, value)
    
    doctest._SpoofOut.write = new_write
