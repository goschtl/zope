"""Testing that grokcore adapters work under Zope2

  >>> from zope import component
  >>> club = component.getUtility(IFiveClub, 'five_inch')
  >>> IFiveClub.providedBy(club)
  True
  >>> isinstance(club, FiveInchClub)
  True

"""
from zope.interface import Interface, implements
from grokcore.component.components import Adapter, GlobalUtility
from grokcore.component.directive import provides, name

class IFiveClub(Interface):
    pass

class ITinyClub(Interface):
    pass

class FiveInchClub(GlobalUtility):
    implements(IFiveClub, ITinyClub)
    provides(IFiveClub)
    name('five_inch')
