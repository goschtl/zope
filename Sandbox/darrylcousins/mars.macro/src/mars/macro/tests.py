import unittest
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    # register macro TALES
    from zope.app.pagetemplate import metaconfigure
    from z3c.macro import tales
    metaconfigure.registerType('macro', tales.MacroExpression)

    # register provider TALES
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('macro.txt',
                             setUp=setUp,
                             optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


