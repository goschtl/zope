from zope.interface import Interface,implements,Attribute
from zope.schema import TextLine,List,Bool,Object,Dict
from zope.schema.interfaces import IField

class ITableAction(Interface):

    """an action that can be applied to a table"""

    def __call__(context):
        """apply itself to context, this is dispatched to the 2
        applyTo* methods by default"""

    def applyToTable(self,table):
        """method applied to table objects"""

    def applyToConfig(self,config):
        """method appied to config objects"""


class ISorter(Interface):

    def sort(items):

        """return the items sorted. items are (key,value) tuples"""

class ITable(Interface):

    def getRows():

        """returns the table rows"""

class IRow(Interface):

    """a table row"""

    key = Attribute('key')

    def getCells():

        """returns the cells of this table"""

class IColumn(Interface):

    """a column"""
    schema = Object(Interface)
    name = TextLine(title=u'Name')
    field = Object(IField)
    title = TextLine(title=u'Title')

class ITableConfig(Interface):

    colNames = List(value_type=IColumn['name'])
    sortBy = TextLine(title=u'Sort by')
    sortReverse = Bool(title=u'Sort reverse')
    columns = Dict(key_type=IColumn['name'],
                   value_type=Object(IColumn))


class ICell(Interface):

    """a cell of a table"""

class ITableForm(Interface):
    
    """a form of a table"""
