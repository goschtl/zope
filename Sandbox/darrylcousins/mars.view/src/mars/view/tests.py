import unittest
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    
    from zope.app.testing import setup
    test.globs = {'root': setup.placefulSetUp(True)}

    import zope.component
    import zope.traversing
    zope.component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
        )

    # register provider TALES
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('view.txt',
                             setUp=setUp,
                             optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')



