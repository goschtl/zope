from zope import schema
from zope.interface import Interface,Attribute
from zope.formlib.interfaces import IAction
from zope.app.i18n import ZopeMessageFactory as _


class IMultiForm(Interface):
    """multiform"""


class IItemForm(Interface):
    """a sub form for an item of a multiform"""


class IGridItemForm(IItemForm):
    """an form for an item of a grid form"""


class IGridForm(IMultiForm):
    """a special grid multiform"""


class IItemAction(IAction):
    """an item action"""

    
class IParentAction(IAction):
    """a parent action"""


class ISelection(Interface):
    """Provides information about the selection state of an object"""

    selected = schema.Bool(title=_(u'Selected'),default=False)


class IFormLocation(Interface):

    __form_name__ = Attribute('The unique name of the item in a multiform')


class ISorter(Interface):

    def sort(items):
        """return the items sorted. items are (key,value) tuples"""


class IFilter(Interface):
    """Provides the content of the context."""

    batch_start = schema.Int()
    
    batch_size = schema.Int()
    
    sort_on = schema.TextLine()
    
    sort_reverse = schema.Bool(default=False)

    sort_columns = schema.List()


class ISubPageMultiform(IMultiForm):
    """A component that displays a part of a page.

    The rendered output must not have a form tag.  It is the
    responsibility of the surrounding page to supply a form tag.

    """

class IPageMultiform(IMultiForm):
    """A component that displays a form as a page.
    """
