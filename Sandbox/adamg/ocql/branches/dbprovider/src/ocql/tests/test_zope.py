import unittest
import doctest

from zope.interface import implements
from zope.component import adapts, getUtility, provideAdapter
from zope.interface import Interface

from ocql.aoptimizer.aoptimizer import AlgebraOptimizer
from ocql.compiler.compiler import AlgebraCompiler
from ocql.database import metadata
from ocql.database.metadata import Metadata
from ocql.engine import OCQLEngine
from ocql.interfaces import IDB
from ocql.parser.queryparser import QueryParser, SymbolContainer 
from ocql.qoptimizer.qoptimizer import QueryOptimizer
from ocql.queryobject.queryobject import *
from ocql.rewriter.rewriter import Rewriter
from ocql.testing.utils import setupInterfaces, setupCatalog
from ocql.tests.test_old import QueryNullParser
from ocql.testing.sample.student import Student
#REMOVE THIS LATER
from ocql.testing.sample.interfaces import IOrganization, IStudent, IMentor, IProject



db = {}

classes = {}

class testZope(unittest.TestCase):
    def setUp(self):
        provideAdapter(QueryParser)
        provideAdapter(QueryNullParser)
        provideAdapter(QueryOptimizer)
        provideAdapter(Rewriter)
        provideAdapter(AlgebraOptimizer)
        provideAdapter(AlgebraCompiler)
        provideAdapter(Metadata)
        
        setupInterfaces(self)
        setupCatalog(self)
        
        self.engine = OCQLEngine()
        
    #just copy following methods from test_old
    def doone(self, query, qo, expected):
        print "==============="
        print "query:",query

        algebra_=qo.rewrite(algebra)

        print "algebra:",algebra_

        code=algebra_.compile();
        compile(code,'<string>','eval')
        q = RunnableQuery(engine,algebra_,code)

        print "code:",code
        print "---------------"
        print "got:     ", q.execute()
        print "expected:", expected

    def doit(self, query, qo, expected):
        run = self.engine.compile(qo)
        result = run.execute()

        self.assertEqual(expected, result)

       
    def test_gsoc(self):
        metadata = IDB(None)
        symbols = SymbolContainer()

        #
        # Simple empty query
        #
        # set [ ]
        #
        query = "set [ ]"
        qo=Query(metadata, symbols,
                 set,
                 [] ,
                 Identifier(metadata, symbols,
                            '') )

        self.doit(query, qo, set([]))
        
        
        symbols = SymbolContainer()
        #
        # Simple SELECT ALL
        #
        # set [ c in ICourse | c ]
        #           
        query = "[c in IStudent | c]"
        qo = Query(
                metadata, symbols,
                set,
                [
                    In(
                       metadata, symbols,
                       Identifier(metadata,symbols,'c'),
                       Identifier(metadata,symbols,'IStudent'))
                ], Identifier(metadata,symbols,'c'))
        
        self.doit(query, qo, set(metadata.db['IStudent']))
        
        
        
def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
                               unittest.makeSuite(testZope),
                               ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
    
