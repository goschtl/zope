from zope.interface import Interface,Attribute
from zope.formlib.interfaces import IAction
from zope import schema
from zope.formlib.i18n import _


class IMultiForm(Interface):

    """multiform"""

class IItemForm(Interface):

    """a sub form for an item of a multiform"""


class IGridItemForm(IItemForm):

    """an form for an item of a grid form"""


class IGridForm(IMultiForm):

    """a special grid multiform"""


class IItemAction(IAction):
    """a item action"""

    
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
