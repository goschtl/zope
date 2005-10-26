import unittest
from zope.app.testing import setup
from zope.app.container.sample import SampleContainer
from zope.interface import Interface,implements,directlyProvides
from zope.app.traversing.interfaces import ITraversable
from zope.schema import Int
from zope.schema.interfaces import IField
from zope.app.container.interfaces import IReadContainer
from zope.containerview.table import Table,SchemaCell,Row,Column,TableConfig
from zope.containerview.table import SchemaSorter,MethodSorter
from zope.containerview.table import IRow,ITable,ICell,IColumn,ISorter
from zope.component import provideAdapter,provideUtility
from zope.app.size.interfaces import ISized
from zope.app.size import DefaultSized
from zope.interface.interfaces import IMethod
from zope.publisher.browser import TestRequest
from zope.app.testing import ztapi
from zope.containerview.table.browser import CellView,TableView
from zope.configuration import xmlconfig
from zope.app.traversing.interfaces import IContainmentRoot
import zope



class ISimple(Interface):

    a = Int(title=u'a')
    b = Int(title=u'b')


class SimpleClass(SampleContainer):

    implements(ISimple,IReadContainer)
    def __init__(self,a,b):
        super(SimpleClass,self).__init__()
        self.a,self.b=a,b

class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        setup.placefulSetUp()
        xmlconfig.file('test.zcml',zope.containerview.table)
        self.container = SampleContainer()
        self.container.__name__ = u'testcontainer'
        directlyProvides(self.container, IContainmentRoot)
        provideAdapter(DefaultSized,(Interface,),ISized)
        
        provideAdapter(MethodSorter,
                       (Interface,IMethod),ISorter)
        provideAdapter(SchemaSorter,
                       (Interface,IField),ISorter)
        provideAdapter(Row,
                       (Interface,IReadContainer,ITable),IRow)
        provideAdapter(SchemaCell,
                       (Interface,IColumn,IRow,ITable),ICell)

        xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <include package="zope.app.component" file="meta.zcml" />
          <view
            for="zope.interface.Interface zope.containerview.table.ICell"
            type="zope.publisher.interfaces.browser.IBrowserRequest"
            factory="zope.containerview.table.browser.CellView"
            provides="zope.containerview.table.browser.ICellView"
            permission="zope.Public"
            name="a"
            />
            <view
            for="zope.interface.Interface zope.containerview.table.ICell"
            type="zope.publisher.interfaces.browser.IBrowserRequest"
            factory="zope.containerview.table.browser.CellView"
            provides="zope.containerview.table.browser.ICellView"
            permission="zope.Public"
            name="b"
            />

            <view
            for="zope.containerview.table.IRow"
            type="zope.publisher.interfaces.browser.IBrowserRequest"
            factory="zope.containerview.table.browser.RowView"
            provides="zope.containerview.table.browser.IRowView"
            permission="zope.Public"
            />
            <view
            for="zope.containerview.table.ITable"
            type="zope.publisher.interfaces.browser.IBrowserRequest"
            factory="zope.containerview.table.browser.TableView"
            provides="zope.containerview.table.browser.ITableView"
            permission="zope.Public"
            />
        </configure>
        """)

        #ztapi.browserView(ICell,u'index',CellView)
        #ztapi.browserView(ITable,u'index',TableView)

    def tearDown(self):
        setup.placefulTearDown()

    def test_1(self):

        self.container[u'first'] = SimpleClass(1,4)
        self.container[u'second'] = SimpleClass(3,2)

        colA = Column(ISimple,u'a')
        colB = Column(ISimple,u'b')
        colSize = Column(ISized,u'size',field=ISized[u'sizeForSorting'])

        table = Table(self.container,u'testtable',[colA,colB,colSize])

        for row in table.getRows():
            self.failUnless(IRow.providedBy(row))
            for cell in row.getCells():
                self.failUnless(ICell.providedBy(cell))
                self.failUnless(cell())

        table.config = TableConfig([u'a',u'b'],sortBy=u'b')
        self.assertEqual(
            list(r.context.b for r in  table.getRows()),[2,4])

        table.config.sortReverse=True
        self.assertEqual(
            list(r.context.b for r in  table.getRows()),[4,2])
        table.config.sortBy = u'size'
        self.assertEqual(
            list(r.context.b for r in  table.getRows()),[4,2])
        request = TestRequest()

        view =  TableView(table,request)
        print "-"*80
        print view()
        print "-"*80


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseTestCase))
    return suite
    
if __name__=="__main__":
    unittest.main()
