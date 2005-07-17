import Zope
from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.tests.test_DirectoryView import skin_path_name
from os.path import join
from Testing.makerequest import makerequest
from Products.PageTemplates.TALES import Undefined

from Products.CMFCore.tests.base.testcase import RequestTest

class DummyCachingManager:
    def getHTTPCachingHeaders( self, content, view_name, keywords ):
        return ( ( 'foo', 'Foo' ), ( 'bar', 'Bar' ) )

class FSPageTemplateTests( RequestTest ):

    def test_Call( self ):
        """
        Test calling works
        """
        script = FSPageTemplate('testPT', join(skin_path_name,'testPT.pt'))
        script = script.__of__(self.root)
        self.assertEqual(script(),'foo\n')

    def test_BadCall( self ):
        """
        Test calling a bad template gives an Undefined exception
        """
        script = FSPageTemplate('testPT', join(skin_path_name,'testPTbad.pt'))
        script = script.__of__(self.root)
        self.assertRaises(Undefined,script)

    def test_caching( self ):
        """
            Test HTTP caching headers.
        """
        self.root.caching_policy_manager = DummyCachingManager()
        original_len = len( self.RESPONSE.headers )
        script = FSPageTemplate('testPT', join(skin_path_name,'testPT.pt'))
        script = script.__of__(self.root)
        script()
        self.failUnless( len( self.RESPONSE.headers ) >= original_len + 2 )
        self.failUnless( 'foo' in self.RESPONSE.headers.keys() )
        self.failUnless( 'bar' in self.RESPONSE.headers.keys() )

def test_suite():
    return TestSuite((
        makeSuite(FSPageTemplateTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')




