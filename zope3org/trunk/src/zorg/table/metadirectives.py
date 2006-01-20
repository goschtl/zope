
from zope.configuration.fields import GlobalInterface,Tokens,Path,Bool
from zope.interface import Interface
from zope.configuration.fields import GlobalObject,PythonIdentifier,Tokens
from zope.schema import TextLine, Int, Id
from zope.app.security.fields import Permission
from interfaces import IColumn


class IColumnDirective(Interface):

    schema = GlobalInterface(required=True)

    name = TextLine(
        title=u'Name',
        required=True)

    field = TextLine(
        title=u'Field Name',
        description=u"""\
        Name of the field to take from schema, defaults to name.
        """,
        required=False)

    title = TextLine(
        title=u'Title',
        required=False)


class ITableConfigDirective(Interface):

    id = Id(required=True)

    colNames = Tokens(
        value_type=IColumnDirective['name'],
        required=False,
        title=u'Column Names')

    sortBy = TextLine(
        title=u'Sort by',
        required=False)

    sortReverse = Bool(
        title=u'Sort reverse',
        required=False)

    batchSize = Int(
        title=u"Maximum rows per page",
        description=u"""
        A value greater than zero splits the grid into single pages.
        """,
        required=False,
        default=0)


class IActionDirective(Interface):
    
    name = TextLine(
        title=u'Name',
        required=True)

    label = TextLine(
        title=u'Label',
        required=False)

    permission = Permission(
        title=u"Permission",
        description=u"""
        The permission that is required in order to display the action.
        """,
        required=False)
        
    forRow = Bool(
        title=u'Action is only available in rows',
        required=False)


class IFilterDirective(Interface):
    
    name = TextLine(
        title=u'Name',
        required=True)
    
    permission = Permission(
        title=u"Permission",
        description=u"""
        The permission that is required in order to display the filter.
        """,
        required=False)
