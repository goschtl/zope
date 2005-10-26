
from zope.configuration.fields import GlobalInterface,Tokens,Path,Bool
from zope.interface import Interface
from zope.configuration.fields import GlobalObject,PythonIdentifier,Tokens
from zope.schema import TextLine,Id
from zope.app.security.fields import Permission
from interfaces import IColumn

class IColumnDirective(Interface):
    schema = GlobalInterface(required=True)
    name = TextLine(title=u'Name',required=True)
    field = TextLine(title=u'Field Name',
                     description=u"""Name of the field to take from
                     schema, defaults to name""",
                     required=False)
    title = TextLine(title=u'Title',required=False)


class ITableConfigDirective(Interface):
    id = Id(required=True)
    colNames = Tokens(value_type=IColumnDirective['name'],
                      required=False,
                      title=u'Column Names')
    sortBy = TextLine(title=u'Sort by',required=False)
    sortReverse = Bool(title=u'Sort reverse',required=False)

class IActionDirective(Interface):
    name = TextLine(title=u'Name',required=True)
    title = TextLine(title=u'Title',required=False)
    class_ = GlobalObject(
        title=u"Class",
        description=u"""an optional class that implements the action""",
        required=False
        )
