import grok
import unittest

def test_suite():
    import grok.admin
    # We must grok our package to get the test registrations...
    grok.grok('grok.admin')
    return grok.testing.test_suite()


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
