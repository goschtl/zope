##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
    Unit tests for CollectorIssue.
"""

import unittest

class CollectorIssueTests( unittest.TestCase ):

    def _makeOne( self, id='foo' ):

        from Products.CMFCollector.CollectorIssue import CollectorIssue

        return CollectorIssue( id=id )

    def assertEquivalentSequences( self, lhs, rhs ):

        lhs = list( lhs )
        rhs = list( rhs )

        self.assertEqual( len( lhs ), len( rhs ) )

        lhs.sort()
        rhs.sort()

        for l, r in map( None, lhs, rhs ):
            self.assertEqual( l, r )

    def testEmpty( self ):

        issue = self._makeOne()

        self.assertEqual( issue.getId(), 'foo' )
        self.assertEqual( issue.Title(), '' )
        self.assertEqual( issue.Description(), '' )

        self.assertEqual( issue.isSecurityRelated(), 0 )
        self.assertEqual( issue.getTopic(), None )
        self.assertEqual( issue.getClassification(), None )
        self.assertEqual( issue.getImportance(), None )
        self.assertEqual( issue.getVersionInfo(), '' )

        self.assertEqual( issue.getSubmitter(), None )
        self.assertEqual( issue.getSubmitterId(), None )
        self.assertEqual( issue.getSubmitterName(), 'Anonymous' )
        self.assertEqual( issue.getSubmitterEmail(), None )

        self.assertEquivalentSequences( [], issue.listSupporters() )
        self.assertEquivalentSequences( [], issue.listKibitzers() )

        from Products.CMFCollector.CollectorIssue import TRANSCRIPT_NAME
        self.assertEquivalentSequences( [TRANSCRIPT_NAME], issue.objectIds() )

        self.assertEqual( issue.objectValues()[0], issue.getTranscript() )
        self.assertEqual( issue.getTranscript(), issue.get_transcript() )

        self.assertEqual( issue.getActionNumber(), 0 )

    def testSecurityRelated( self ):

        from Products.CMFCollector.CollectorIssue import CollectorIssue

        issue = self._makeOne()
        issue.setSecurityRelated( '' )
        self.failIf( issue.isSecurityRelated() )

        issue = self._makeOne()
        issue.setSecurityRelated( None )
        self.failIf( issue.isSecurityRelated() )

        issue = self._makeOne()
        issue.setSecurityRelated( 0 )
        self.failIf( issue.isSecurityRelated() )

        issue = self._makeOne()
        issue.setSecurityRelated( '1' )
        self.failUnless( issue.isSecurityRelated() )

        issue = self._makeOne()
        issue.setSecurityRelated( 1 )
        self.failUnless( issue.isSecurityRelated() )

    def test_setTopic( self ):

        issue = self._makeOne()
        issue.setTopic( 'Foo' )
        self.assertEqual( issue.getTopic(), 'Foo' )

    def test_setClassification( self ):

        issue = self._makeOne()
        issue.setClassification( 'Foo' )
        self.assertEqual( issue.getClassification(), 'Foo' )

    def test_setImportance( self ):

        issue = self._makeOne()
        issue.setImportance( 'Foo' )
        self.assertEqual( issue.getImportance(), 'Foo' )

    def test_setVersionInfo( self ):

        issue = self._makeOne()
        issue.setVersionInfo( 'Foo' )
        self.assertEqual( issue.getVersionInfo(), 'Foo' )

    def test_setSubmitter_idempotent( self ):

        issue = self._makeOne()

        changes = issue.setSubmitter()
        self.assertEqual( changes, [] )

        self.assertEqual( issue.getSubmitter(), None )
        self.assertEqual( issue.getSubmitterId(), None )
        self.assertEqual( issue.getSubmitterName(), 'Anonymous' )
        self.assertEqual( issue.getSubmitterEmail(), None )

    def test_setSubmitter_id_only( self ):

        issue = self._makeOne()

        changes = issue.setSubmitter( submitter_id='joe' )
        self.assertEquivalentSequences( changes
                                      , [ "submitter id: 'None' => 'joe'" ]
                                      )

        self.assertEqual( issue.getSubmitter(), None )
        self.assertEqual( issue.getSubmitterId(), 'joe' )
        self.assertEqual( issue.getSubmitterName(), 'joe' )
        self.assertEqual( issue.getSubmitterEmail(), None )

    def test_setSubmitter_name_only( self ):

        issue = self._makeOne()

        changes = issue.setSubmitter( submitter_name='Joe' )
        self.assertEquivalentSequences( changes
                                      , [ 'submitter name' ]
                                      )

        self.assertEqual( issue.getSubmitter(), None )
        self.assertEqual( issue.getSubmitterId(), None )
        self.assertEqual( issue.getSubmitterName(), 'Joe' )
        self.assertEqual( issue.getSubmitterEmail(), None )

    def test_setSubmitter_email_only( self ):

        issue = self._makeOne()

        changes = issue.setSubmitter( submitter_email='joe@byword.com' )
        self.assertEquivalentSequences( changes
                                      , [ 'submitter email' ]
                                      )

        self.assertEqual( issue.getSubmitter(), None )
        self.assertEqual( issue.getSubmitterId(), None )
        self.assertEqual( issue.getSubmitterName(), 'Anonymous' )
        self.assertEqual( issue.getSubmitterEmail(), 'joe@byword.com' )

    def test_supporters( self ):

        issue = self._makeOne()

        issue.addSupporter( 'joe' )
        self.assertEquivalentSequences( [ 'joe' ]
                                      , issue.listSupporters() )

        issue.addSupporter( 'ally' )
        issue.addSupporter( 'zeb' )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'zeb' ]
                                      , issue.listSupporters() )

        issue.removeSupporter( 'joe' )
        self.assertEquivalentSequences( [ 'ally', 'zeb' ]
                                      , issue.listSupporters() )

        issue.clearSupporters()
        self.assertEquivalentSequences( []
                                      , issue.listSupporters() )

        changes = issue.setSupporters( [ 'joe', 'ally', 'zeb' ] )
        self.assertEquivalentSequences( [ 'added supporters: joe ally zeb' ]
                                      , changes )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'zeb' ]
                                      , issue.listSupporters() )

        changes = issue.setSupporters( [ 'joe', 'ally', 'fran' ] )
        self.assertEquivalentSequences( [ 'added supporters: fran'
                                        , 'removed supporters: zeb'
                                        ]
                                      , changes )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'fran' ]
                                      , issue.listSupporters() )

    def test_kibitzers( self ):

        issue = self._makeOne()

        issue.addKibitzer( 'joe' )
        self.assertEquivalentSequences( [ 'joe' ]
                                      , issue.listKibitzers() )

        issue.addKibitzer( 'ally' )
        issue.addKibitzer( 'zeb' )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'zeb' ]
                                      , issue.listKibitzers() )

        issue.removeKibitzer( 'joe' )
        self.assertEquivalentSequences( [ 'ally', 'zeb' ]
                                      , issue.listKibitzers() )

        issue.clearKibitzers()
        self.assertEquivalentSequences( []
                                      , issue.listKibitzers() )

        changes = issue.setKibitzers( [ 'joe', 'ally', 'zeb' ] )
        self.assertEquivalentSequences( [ 'added kibitzers: joe ally zeb' ]
                                      , changes )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'zeb' ]
                                      , issue.listKibitzers() )

        changes = issue.setKibitzers( [ 'joe', 'ally', 'fran' ] )
        self.assertEquivalentSequences( [ 'added kibitzers: fran'
                                        , 'removed kibitzers: zeb'
                                        ]
                                      , changes )
        self.assertEquivalentSequences( [ 'joe', 'ally', 'fran' ]
                                      , issue.listKibitzers() )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( CollectorIssueTests ) )
    return suite

def run():
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    run()
