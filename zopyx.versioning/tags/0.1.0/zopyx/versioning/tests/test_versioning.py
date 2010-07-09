import unittest2
from zope.interface.verify import verifyClass

from zopyx.versioning.interfaces import IVersioning
from zopyx.versioning import facade


class VersioningTests(unittest2.TestCase):

    def testIFace(self):
        verifyClass(IVersioning, facade.VersioningFacade)

