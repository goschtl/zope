##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
import os, sys
        
sys.path.insert(0, os.getcwd())
try: import unittest
except:
    sys.path[0]=os.path.join(sys.path[0],'..','..')
    import unittest

import ZODB
from SearchIndex.UnKeywordIndex import UnKeywordIndex

class Dummy:

    def __init__( self, foo ):
        self._foo = foo

    def foo( self ):
        return self._foo
    
    def __str__( self ):
        return '<Dummy: %s>' % self._foo
    
    __repr__ = __str__

class TestCase( unittest.TestCase ):
    """
        Test KeywordIndex objects.
    """

    def setUp( self ):
        """
        """
        self._index = UnKeywordIndex( 'foo' )
        self._marker = []
        self._values = [ ( 0, Dummy( ['a'] ) )
                       , ( 1, Dummy( ['a','b'] ) )
                       , ( 2, Dummy( ['a','b','c'] ) )
                       , ( 3, Dummy( ['a','b','c', 'a'] ) )
                       , ( 4, Dummy( ['a', 'b', 'c', 'd'] ) )
                       , ( 5, Dummy( ['a', 'b', 'c', 'e'] ) )
                       , ( 6, Dummy( ['a', 'b', 'c', 'e', 'f'] ))
                       , ( 7, Dummy( [0] ) ) 
                       ]
        self._noop_req  = { 'bar': 123 }
        self._all_req = { 'foo': ['a'] }
        self._some_req = { 'foo': ['e'] }
        self._overlap_req = { 'foo': ['c', 'e'] }
        self._string_req = {'foo': 'a'}
        self._zero_req  = { 'foo': [0] }

    def tearDown( self ):
        """
        """

    def _populateIndex( self ):
        for k, v in self._values:
            self._index.index_object( k, v )

    def _checkApply( self, req, expectedValues ):
        result, used = self._index._apply_index( req )
        assert used == ( 'foo', )
        assert len(result) == len( expectedValues ), \
          '%s | %s' % ( map( None, result ),
                        map(lambda x: x[0], expectedValues ))

        if hasattr(result, 'keys'): result=result.keys()
        for k, v in expectedValues:
            assert k in result

    def testAddObjectWOKeywords(self):


        import zLOG

        def log_write(subsystem, severity, summary, detail, error,
                      PROBLEM=zLOG.PROBLEM):
            if severity >= PROBLEM:
                assert 0, "%s(%s): %s" % (subsystem, severity, summary)

        old_log_write=zLOG.log_write
        zLOG.log_write=log_write
        try:
            self._populateIndex()
            self._index.index_object(999, None)
        finally:
            zLOG.log_write=old_log_write
    
    def testEmpty( self ):
        assert len( self._index ) == 0
        assert len( self._index.referencedObjects() ) == 0

        assert self._index.getEntryForObject( 1234 ) is None
        assert ( self._index.getEntryForObject( 1234, self._marker )
                  is self._marker ), self._index.getEntryForObject(1234)
        self._index.unindex_object( 1234 ) # nothrow

        assert self._index.hasUniqueValuesFor( 'foo' )
        assert not self._index.hasUniqueValuesFor( 'bar' )
        assert len( self._index.uniqueValues( 'foo' ) ) == 0

        assert self._index._apply_index( self._noop_req ) is None
        self._checkApply( self._all_req, [] )
        self._checkApply( self._some_req, [] )
        self._checkApply( self._overlap_req, [] )
        self._checkApply( self._string_req, [] )
        
    def testPopulated( self ):
        self._populateIndex()
        values = self._values

        #assert len( self._index ) == len( values )
        assert len( self._index.referencedObjects() ) == len( values )

        assert self._index.getEntryForObject( 1234 ) is None
        assert ( self._index.getEntryForObject( 1234, self._marker )
                  is self._marker )
        self._index.unindex_object( 1234 ) # nothrow

        for k, v in values:
            assert self._index.getEntryForObject( k ) == v.foo()

        assert (len( self._index.uniqueValues( 'foo' ) ) == len( values )-1,
                len(values)-1)

        assert self._index._apply_index( self._noop_req ) is None

        self._checkApply( self._all_req, values[:-1])
        self._checkApply( self._some_req, values[ 5:7 ] )
        self._checkApply( self._overlap_req, values[2:7] )
        self._checkApply( self._string_req, values[:-1] )

    def testZero( self ):
        self._populateIndex()
        values = self._values
        self._checkApply( self._zero_req, values[ -1: ] )
        assert 0 in self._index.uniqueValues( 'foo' )


def test_suite():
    return unittest.makeSuite( TestCase )

def main():
    unittest.TextTestRunner().run( test_suite() )

def debug():
    test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        main()
    
