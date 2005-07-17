import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.FSPythonScript import FSPythonScript
from Products.CMFCore.tests.base.testcase import FSDVTest
from os.path import join

class FSPythonScriptTests( FSDVTest ):

    def test_GetSize( self ):
        """ Test get_size returns correct value """
        script = FSPythonScript('test1', join(self.skin_path_name,'test1.py'))
        self.assertEqual(len(script.read()),script.get_size())

def test_suite():
    return TestSuite((
        makeSuite(FSPythonScriptTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')




