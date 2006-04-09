from zope.interface import Interface
from zope.formlib.interfaces import IAction

class IMultiForm(Interface):

    """multiform"""


class IParentAction(IAction):
    """a parent action"""
