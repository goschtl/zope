from zope.testing.doctest import DocFileSuite

def test_suite():
    return DocFileSuite('README.txt')


