
from zope.interface import Interface, implements, Attribute
from zope.schema import TextLine, List, Bool, Object, Dict, Int
from zope.schema.interfaces import IField


class ISorter(Interface):

    def sort(items):
        """return the items sorted. items are (key,value) tuples"""


class ITable(Interface):

    def getRows():
        """returns the table rows"""

    def getActions():
        """returns the table actions"""


class IRow(Interface):
    """a table row"""

    key = Attribute('key')

    def getCells():
        """returns the cells of this table"""

    def getActions():
        """returns the row actions"""


class IColumn(Interface):
    """a column"""
    
    schema = Object(Interface)
    name = TextLine(title=u'Name')
    field = Object(IField)
    title = TextLine(title=u'Title')
    sorter = Object(ISorter)


class IAction(Interface):
    """a action of a table"""

    name = TextLine(
        title=u'Name',
        required=True)

    label = TextLine(
        title=u'Label',
        required=False)

    forRow = Bool(
        title=u'Action is only available in rows',
        required=False)


class IFilter(Interface):
    """a filter of a table"""

    name = TextLine(
        title=u'Name',
        required=True)
 

class ITableConfig(Interface):

    colNames = List(
        value_type=IColumn['name'])

    sortBy = TextLine(
        title=u'Sort by')

    sortReverse = Bool(
        title=u'Sort reverse')

    batchSize = Int(
        title=u"Maximum rows per page",
        description=u"""
        A value greater than zero splits the grid into single pages.
        """,
        required=False,
        default=0)

    columns = Dict(
        key_type=IColumn['name'],
        value_type=Object(IColumn))

    actions = Dict(
        key_type=IAction['name'],
        value_type=Object(IAction))

    filters = Dict(
        key_type=IFilter['name'],
        value_type=Object(IFilter))


class ITableAction(Interface):
    """a action of a table"""

    container = Object(Interface)
    table = Object(ITableConfig)
    action = Object(IAction)
    name = IAction['name']
    label = IAction['label']


class ITableFilter(Interface):
    """a filter of a table"""

    container = Object(Interface)
    table = Object(ITableConfig)
    filter = Object(IFilter)
    name = IFilter['name']
    

class ICell(Interface):
    """a cell of a table"""


class ITableForm(Interface):
    """a form of a table"""
