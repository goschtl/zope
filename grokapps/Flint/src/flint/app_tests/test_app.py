"""
Do a Python test on the app.
:Test-Layer: python
"""
import unittest
from flint.app import Flint

class FlintSmokeTest(unittest.TestCase):
    """ Test that the Flint application can be instantiated. """

    def test1(self):
        """ test that something works """
        grokapp = Flint()
        self.assertEqual(list(grokapp.keys()), [])

