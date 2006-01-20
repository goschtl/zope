
from zope.interface import Interface


class ITableForm(Interface):
    """a table multiform"""

class ITableView(Interface):
    """table view"""

class IRowView(Interface):
    """row view"""

class ICellView(Interface):
    """cell view"""    

class IActionView(Interface):
    """action view"""    

class IFilterView(Interface):
    """filter view"""
    
    def filter():
        """will be evaluated upon display the rows."""

    