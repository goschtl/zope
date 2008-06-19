import unittest
import doctest
from zope.component.interface import searchInterfaceUtilities 
from zope.interface import implements
from zope.component import adapts, getUtility, provideAdapter
from ocql.interfaces import IDB 
from ocql.database import metadata
from zope.interface import Interface
from zope.app.catalog.interfaces import ICatalog
from ocql.testing.utils import setupInterfaces, setupCatalog
from zope.location import LocationProxy
from zope.app.intid import IIntIds
from ocql.parser.queryparser import QueryParser, SymbolContainer
from ocql.tests.test_old import QueryNullParser
from ocql.qoptimizer.qoptimizer import QueryOptimizer
from ocql.rewriter.rewriter import Rewriter
from ocql.aoptimizer.aoptimizer import AlgebraOptimizer
from ocql.compiler.compiler import AlgebraCompiler
from ocql.testing.gsocdatabase import GsocMetadata
from ocql.testing.sample.student import Student

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
        
        setupInterfaces(self)
        setupCatalog(self)
        #import pydevd;pydevd.settrace()
        items = list(searchInterfaceUtilities(self))
        catalog = getUtility(ICatalog,name='foo-catalog')
        
        intids = getUtility(IIntIds)
        #is there is a way to find all the indexes
        results = catalog.apply({'student_name':('A','Z')})
        
        student_list = []
        for r in results:
            obj = intids.getObject(r)
            print obj.__class__.__name__          
            student_list.append(obj)

        db.__setitem__('student_name', student_list)

        for item in items:
            print item
            class_name = item[0].rsplit('.',1)[1].__str__()
            classes.__setitem__(class_name,class_name)
           # print item[1].__class__

        GsocMetadata()
        provideAdapter(GsocMetadata)
        
           
    def test_gsoc(self):
        print "loading..."
        metadata = IDB(None)
        symbols = SymbolContainer()
        
        
    
    
        
def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
                               unittest.makeSuite(testZope),
                               ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
    
