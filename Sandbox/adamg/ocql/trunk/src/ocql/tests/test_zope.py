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
from ocql.testing.utils import setupInterfaces, setupCatalog, setupAdapters
from ocql.tests.test_old import QueryNullParser
from ocql.testing.sample.student import Student
import ocql.compiler.compiler
import ocql.rewriter.rewriter

db = {}

classes = {}

class testZope(unittest.TestCase):
    def setUp(self):
        setupAdapters(self)
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
        qo=Head(Query(metadata, symbols,
                 set,
                 [] ,
                 Identifier(metadata, symbols,
                            '') ))

        self.doit(query, qo, set([]))


        symbols = SymbolContainer()
        #
        # Simple empty query
        #
        # list [ ]
        #
        query = "list [ ]"
        qo=Head(Query(metadata, symbols,
                 list,
                 [] ,
                 Identifier(metadata, symbols,
                            '') ))

        self.doit(query, qo, [])


        symbols = SymbolContainer()
        #
        # Simple SELECT ALL
        #
        # set [ c in IStudent | c ]
        #
        query = "set [c in IStudent | c]"
        qo = Head(Query(
                metadata, symbols,
                set,
                [
                    In(
                       metadata, symbols,
                       Identifier(metadata,symbols,'c'),
                       Identifier(metadata,symbols,'IStudent'))
                ], Identifier(metadata,symbols,'c')))

        self.doit(query, qo, set(metadata.getAll('IStudent')))


        symbols = SymbolContainer()
        #
        # Selecting a property
        #
        # set [ c in IStudent | c.name ]
        #
        query = "set [c in IStudent | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata, symbols,'c'),
                           Identifier(metadata, symbols, 'IStudent'))
                    ],Identifier(metadata, symbols, 'c.name')))
        self.doit(query, qo, set(["Charith", "Jane", "Ann", "Stewart"]))


        symbols = SymbolContainer()
        #
        # Filtering --one result
        #
        # set [ c in IProject; c.description="test" | c.name]
        #
        query = "set [c in IProject; c.description==test | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IProject')),
                        Eq(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.description'),
                           Identifier(metadata, symbols, '"test"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set(["Save the world"]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country="USA" | c.name]
        #
        query = "set [c in IStudent; c.country==USA | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Eq(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"USA"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([metadata.getFromIndex('IStudent', 'country','==', 'USA')[0].name]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country!="USA" | c.name]
        #
        query = "[c in IStudent; c.country != USA | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Ne(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"USA"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([i.name for i in metadata.getFromIndex('IStudent', 'country','!=', 'USA')]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country <= "Sri Lanka" | c.name]
        #
        query = "set [c in IStudent; c.country <= 'Sri Lanka' | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Le(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"Sri Lanka"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([i.name for i in metadata.getFromIndex('IStudent', 'country','<=', 'Sri Lanka')]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country >= "Sri Lanka" | c.name]
        #
        query = "set [c in IStudent; c.country >= 'Sri Lanka' | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Ge(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"Sri Lanka"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([i.name for i in metadata.getFromIndex('IStudent', 'country','>=', 'Sri Lanka')]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country < "Sri Lanka" | c.name]
        #
        query = "set [c in IStudent; c.country < 'Sri Lanka' | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Lt(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"Sri Lanka"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([i.name for i in metadata.getFromIndex('IStudent', 'country','<', 'Sri Lanka')]))


        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent; c.country > "Sri Lanka" | c.name]
        #
        query = "set [c in IStudent; c.country > 'Sri Lanka' | c.name]"
        qo = Head(Query(
                   metadata, symbols,
                   set,
                   [
                        In(
                           metadata, symbols,
                           Identifier(metadata,symbols,'c'),
                           Identifier(metadata,symbols, 'IStudent')),
                        Gt(
                           metadata,symbols,
                           Identifier(metadata, symbols, 'c.country'),
                           Identifier(metadata, symbols, '"Sri Lanka"'))
                   ], Identifier(metadata, symbols, 'c.name')))

        self.doit(query, qo, set([i.name for i in metadata.getFromIndex('IStudent', 'country','>', 'Sri Lanka')]))


        symbols = SymbolContainer()
        #
        #
        # join -- Mentor who is mentoring Hungary student
        #
        # set [ m in IMentor; every set [ s in IStudent; some s.mentor == m | s.country ] == Hungary  | m.name ]
        #
        query = """set [ m in IMentor;
            every
            set [ s in IStudent; some s.mentor == m; s.country == Hungary | s.name] == Stewart
            | m.name ]"""
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'m'),
                    Identifier(metadata, symbols,'IMentor')),
                Eq(
                    metadata, symbols,
                    Quanted(
                        metadata, symbols,
                        Every(metadata, symbols, ''),
                        Query(
                            metadata, symbols,
                            set,
                            [
                                In(
                                    metadata, symbols,
                                    Identifier(metadata, symbols,'s'),
                                    Identifier(metadata, symbols,'IStudent')),
                                Eq(
                                    metadata,symbols,
                                    Identifier(metadata, symbols, 's.country'),
                                    Identifier(metadata, symbols, '"Hungary"')),
                                Eq(
                                    metadata, symbols,
                                    Identifier(metadata, symbols,'m'),
                                    Quanted(
                                        metadata, symbols,
                                        Some(metadata, symbols, ''),
                                        Property(metadata, symbols,
                                            Identifier(metadata, symbols, 's'),
                                            Identifier(metadata, symbols, 'mentor'))
                                        ))
                            ], Identifier(metadata, symbols, 's.name'))
                    ),Constant(metadata, symbols,'Stewart')),
            ] ,Identifier(metadata, symbols,'m.name')))

        self.doit(query, qo, set(['John Doe']))


def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
                               unittest.makeSuite(testZope),
                               ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
