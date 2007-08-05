import unittest

class TestAPI(unittest.TestCase):
    """
    Make sure that five.publication's request and response support the
    same (legacy) API as ZPublisher.
    """

    def test_get_header(self):
        pass # TODO


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAPI))
    return suite
