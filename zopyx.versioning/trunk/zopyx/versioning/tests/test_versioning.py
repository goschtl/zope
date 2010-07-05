import unittest2
from zope.interface.verify import verifyClass

from interfaces import IVersioning
import facade


class VersioningTests(unittest2.TestCase):

    def testIFace(self):
        verifyClass(IVersioning, facade.VersioningFacade)

