# -*- coding: UTF-8 -*-

"""OLD tests taken over

$Id$
"""

import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements

from ocql.queryobject.queryobject import *
from ocql.parser.queryparser import SymbolContainer
from ocql.rewriter import algebra
from ocql.engine import OCQLEngine
from ocql.compiler.runnablequery import RunnableQuery

from ocql.parser.queryparser import QueryParser
from ocql.qoptimizer.qoptimizer import QueryOptimizer
from ocql.rewriter.rewriter import Rewriter
from ocql.aoptimizer.aoptimizer import AlgebraOptimizer
from ocql.compiler.compiler import AlgebraCompiler
from ocql.testing.database import TestMetadata
from ocql.testing.utils import setupInterfaces, setupCatalog, setupAdapters

import ocql.compiler.compiler
import ocql.rewriter.rewriter

from ocql.testing.database import C1, C2, C3
from ocql.testing.database import D1, D2, D3

from ocql.interfaces import IDB
from ocql.interfaces import IQueryParser
from ocql.interfaces import IObjectQueryHead


class QueryNullParser(object):
    implements(IQueryParser)
    adapts(IObjectQueryHead)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        return self.context


class testOLD(unittest.TestCase):
    def setUp(self):
        setupAdapters(self)
        provideAdapter(TestMetadata)

        self.engine = OCQLEngine()

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


    def test_old(self):
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
        # Simple SELECT ALL
        #
        # set [ c in ICourse | c ]
        #
        query = "[ c in ICourse | c ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
            ] ,Identifier(metadata, symbols,'c') ))

        #caution, these here are object references
        self.doit(query, qo, set([ C1 , C2, C3 ]))


        symbols = SymbolContainer()
        #
        # Selecting a property
        #
        # set [ c in ICourse | c.code ]
        #
        query = "[ c in ICourse | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
            ] ,Identifier(metadata, symbols,'c.code') ))

        self.doit(query, qo, set([ "C1" , "C2", "C3"  ]))


        symbols = SymbolContainer()
        #
        # Filtering -- empty result
        #
        # set [ c in ICourse , c.credits>3 | c.code ]
        #
        query = "[ c in ICourse, c.credits>3 | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Gt(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
            ] ,Identifier(metadata, symbols, 'c.code') ))

        #from pub.dbgpclient import brk; brk('172.16.144.39')


        self.doit(query, qo, set([]))


        symbols = SymbolContainer()
        #
        # Filtering -- full result
        #
        # set [ c in ICourse , c.credits<=3 | c.code ]
        #
        query = "[ c in ICourse, c.credits<=3 | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set, [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Le(metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
            ] ,Identifier(metadata, symbols,'c.code')))

        self.doit(query, qo, set([ "C1" , "C2", "C3" ]))


        symbols = SymbolContainer()
        #
        # Filtering -- one result
        #
        # set [ c in ICourse , c.credits=3 | c.code ]
        #
        query = "[ c in ICourse, c.credits=3 | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
            ] ,Identifier(metadata, symbols,'c.code')))

        self.doit(query, qo, set([ "C2", "C3" ]))


        symbols = SymbolContainer()
        #
        # Two filters -- full results
        #
        # set [ c in ICourse , c.credits<5, c.credits >=1  | c.code ]
        #
        query = "[ c in ICourse, c.credits<3, c.credits>=1 | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Lt(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'5')),
                Ge(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'1')),
            ] ,Identifier(metadata, symbols, 'c.code')))

        self.doit(query, qo, set([ "C1", "C2", "C3" ]))


        symbols = SymbolContainer()
        #
        # Two filters -- one result
        #
        # set [ c in ICourse , c.credits<=2, 2<=c.credits  | c.code ]
        #
        query = "[ c in ICourse, c.credits<=2, 2<=c.credits | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set, [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Le(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'2')),
                Le(
                    metadata, symbols,
                    Constant(metadata, symbols,'2'),
                    Identifier(metadata, symbols,'c.credits')),
            ] ,Identifier(metadata, symbols,'c.code')))

        self.doit(query, qo, set([ "C1" ]))


        symbols = SymbolContainer()
        #
        # Two filters -- one result
        #
        # set [ c in ICourse , c.credits>=2, 2>=c.credits  | c.code ]
        #
        query = "[ c in ICourse, c.credits>=2, 2>=c.credits | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set, [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Ge(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'2')),
                Ge(
                    metadata, symbols,
                    Constant(metadata, symbols,'2'),
                    Identifier(metadata, symbols,'c.credits')),
            ] ,Identifier(metadata, symbols,'c.code')))

        self.doit(query, qo, set([ "C1" ]))


        symbols = SymbolContainer()
        #
        # Two filters -- no result
        #
        # set [ c in ICourse , c.credits=3, c.credits!=3  | c.code ]
        #
        query = "[ c in ICourse, c.credits=3, c.credits!=3 | c.code ]"
        qo=Head(Query(
            metadata, symbols,
            set, [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
                Ne(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
            ] ,Identifier(metadata, symbols,'c.code')))

        self.doit(query, qo, set([]))


        symbols = SymbolContainer()
        #
        # join -- Departments running curses
        #
        # set [ c in ICourse d, in IDepartment ,
        # some c.runBy = d  | d.name ]
        #
        query = "[ c in ICourse, d in IDepartment, d = some c.runBy | d.name  ]"
        qo=Head(Query(
            metadata, symbols,
            set, [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Identifier(metadata, symbols,'IDepartment')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Quanted(metadata, symbols,
                            Some(metadata, symbols, ''),
                            Property(metadata, symbols,
                                    Identifier(metadata, symbols, 'c'),
                                    Identifier(metadata, symbols, 'runBy'))
                                )),
            ] ,Identifier(metadata, symbols,'d.name')))

        self.doit(query, qo, set(['Other department', 'Computing Science']))


        symbols = SymbolContainer()
        #
        # join -- Departments running some 3 credits curses
        #
        # set [ d in ICourse, c in ICourse, c.credits=3, some c.runBy = d | d.name ]
        #
        query = "[ c in ICourse, d in IDepartment, c.credits=3, d = some c.runBy | d.name  ]"
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Identifier(metadata, symbols,'IDepartment')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c.credits'),
                    Constant(metadata, symbols,'3')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Quanted(
                        metadata, symbols,
                        Some(metadata, symbols, ''),
                        Property(metadata, symbols,
                                    Identifier(metadata, symbols, 'c'),
                                    Identifier(metadata, symbols, 'runBy'))
                                )),
            ] ,Identifier(metadata, symbols, 'd.name')))

        self.doit(query, qo, set(['Computing Science']))


        symbols = SymbolContainer()
        # join -- Departments running some not 3 credits curses
        #
        # [ d in IDepartment, c in ICourse, some c.runBy = d, some c.credits != 3| d.name ]
        #
        query = """[ d in IDepartment,
        c in ICourse,
        some c.runBy = d, c.credits != 3| d.name ]"""
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Identifier(metadata, symbols,'IDepartment')),
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Eq(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Quanted(
                        metadata, symbols,
                        Some(metadata, symbols, ''),
                        Property(metadata, symbols,
                                    Identifier(metadata, symbols, 'c'),
                                    Identifier(metadata, symbols, 'runBy'))
                                )),
                Ne(
                    metadata, symbols,
                    Constant(metadata, symbols,'3'),
                    Identifier(metadata, symbols,'c.credits')),
            ] ,Identifier(metadata, symbols,'d.name')))

        self.doit(query, qo, set(['Other department','Computing Science']))


        symbols = SymbolContainer()
        #
        #
        # join -- Departments running just 2 credits curses
        #
        # set [ d in IDepartment, every set [ c in ICourse, some c.runBy = d | c.credits ] = 3  | d.name ]
        #
        query = """set [ d in IDepartment,
            every
            set [ c in ICourse, some c.runBy = d | c.credits ] = 2
            | d.name ]"""
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'d'),
                    Identifier(metadata, symbols,'IDepartment')),
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
                                    Identifier(metadata, symbols,'c'),
                                    Identifier(metadata, symbols,'ICourse')),
                                Eq(
                                    metadata, symbols,
                                    Identifier(metadata, symbols,'d'),
                                    Quanted(
                                        metadata, symbols,
                                        Some(metadata, symbols, ''),
                                        Property(metadata, symbols,
                                            Identifier(metadata, symbols, 'c'),
                                            Identifier(metadata, symbols, 'runBy'))
                                        )),
                            ], Identifier(metadata, symbols, 'c.credits')
                            )
                    ),Constant(metadata, symbols,'2')),
            ] ,Identifier(metadata, symbols,'d.name')))

        self.doit(query, qo, set(['Other department']))


        symbols = SymbolContainer()
        #
        #
        # alias
        #
        # set [ c in ICourse, a as c.code  | a ]
        #
        query = """set [ c in ICourse, a as c.code  | a ]"""
        qo=Head(Query(
            metadata, symbols,
            set,
            [
                In(
                    metadata, symbols,
                    Identifier(metadata, symbols,'c'),
                    Identifier(metadata, symbols,'ICourse')),
                Alias(
                    metadata, symbols,
                    Identifier(metadata, symbols,'a'),
                    Property(metadata, symbols,
                         Identifier(metadata, symbols, 'c'),
                         Identifier(metadata, symbols, 'code')))
            ] ,Identifier(metadata, symbols,'a')))

        self.doit(query, qo, set(['C1','C2','C3']))

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(testOLD),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')