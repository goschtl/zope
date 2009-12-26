import doctest

def test_suite():
    return doctest.DocTestSuite(
        'z3c.i18n.iso',
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        )
