import unittest
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('./contentprovider.txt',
                             setUp=setUp,
                             optionflags=optionflags),
                   ])

    return suite



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


