from zope.app.testing import functional

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        'demo/README.txt',
        )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
