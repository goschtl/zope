import unittest


class TestDummy(unittest.TestCase):

    def test_base(self):
        self.failIf(1 != 1)


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestDummy)
