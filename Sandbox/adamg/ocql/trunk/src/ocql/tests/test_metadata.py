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
from ocql.exceptions import ReanalyzeRequired
import ocql.compiler.compiler
import ocql.rewriter.rewriter

class testMetadata(unittest.TestCase):
    def setUp(self):
        setupAdapters(self)
        setupInterfaces(self)
        setupCatalog(self)

        self.engine = OCQLEngine()

    def test_metadata_reanalyze(self):
        #check to see how ReanalyzeRequired works
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

        try:
            run = self.engine.compile(qo)
            self.assert_('metadata.getFromIndex("IStudent", "country", "==", "USA"))' in run.code)

            self.delete_index('student_country')

            #no reanalyze here, raises exception
            result = run.execute(noretry=True)

            self.fail("ReanalyzeRequired expected")
        except ReanalyzeRequired:
            pass

        #reanalyze here, no exception, returns result
        result = run.execute()

        #code changes
        self.assert_('metadata.getAll("IStudent"))' in run.code)



    def delete_index(self, todel):
        metadata = IDB(None)
        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        for name, catalog in catalogs:
            for iname, index in catalog.items():
                if iname == todel:
                    del catalog[iname]

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(testMetadata),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')