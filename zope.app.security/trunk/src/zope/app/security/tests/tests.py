import os
import zope.app.testing.functional
import unittest

here = os.path.realpath(os.path.dirname(__file__))
PermissionsLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(here, "ftesting.zcml"), __name__,
    "PermissionsLayer")

def test_suite():
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        'persistentlist.txt')
    suite.layer = PermissionsLayer
    return unittest.TestSuite([suite])
