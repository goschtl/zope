# -*- coding: UTF-8 -*-

import unittest
import doctest

from zope.component import getUtilitiesFor
from zope.app.catalog.interfaces import ICatalog
from zope.component import getUtility, provideAdapter
from zope.app.intid import IIntIds
from zope.app.catalog.field import FieldIndex

from ocql.aoptimizer.aoptimizer import AlgebraOptimizer
from ocql.compiler.compiler import AlgebraCompiler
from ocql.compiler.compiler import registerAdapters
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
import ocql.compiler.compiler
import ocql.rewriter.rewriter

class testMetadata(unittest.TestCase):
    def setUp(self):
        provideAdapter(QueryParser)
        provideAdapter(QueryNullParser)
        provideAdapter(QueryOptimizer)
        provideAdapter(Rewriter)
        provideAdapter(AlgebraOptimizer)
        provideAdapter(AlgebraCompiler)
        provideAdapter(Metadata)
        ocql.compiler.compiler.registerAdapters()
        ocql.rewriter.rewriter.registerAdapters()
        setupInterfaces(self)
        setupCatalog(self)

        self.engine = OCQLEngine()

    def compare(self, qo, expected):
        run = self.engine.compile(qo)
        self.delete_index()
        result = run.execute()

        #self.assertEqual(expected, result)

    def test_metadata(self):
        metadata = IDB(None)

        symbols = SymbolContainer()
        #
        # Filtering --one result using optimization
        #
        # set [ c in IStudent , c.country="USA" | c.name]
        #
        query = "[c in IStudent , c.country=USA | c.name]"
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

        self.compare(qo, "Traceback (most recent call last): ....")
#set([metadata.getFromIndex('IStudent', 'country','==', 'USA')[0].name])

    def delete_index(self):
        """
        >>> delete_index()
        Traceback (most recent call last):
        ...
        """
        metadata = IDB(None)
        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        for name, catalog in catalogs:
            for iname, index in catalog.items():
                if iname == 'student_country':
                    del catalog[iname]

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(testMetadata),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')