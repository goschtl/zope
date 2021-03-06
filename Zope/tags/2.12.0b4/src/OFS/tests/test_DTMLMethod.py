import unittest

class DTMLMethodTests(unittest.TestCase):

    def _getTargetClass(self):
        from OFS.DTMLMethod import DTMLMethod
        return DTMLMethod

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_IWriteLock(self):
        from zope.interface.verify import verifyClass
        from webdav.interfaces import IWriteLock
        verifyClass(IWriteLock, self._getTargetClass())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DTMLMethodTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
