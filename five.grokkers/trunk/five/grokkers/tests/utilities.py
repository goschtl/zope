"""Testing that grokcore adapters work under Zope2

  >>> from zope import component
  >>> club = component.getUtility(IFiveClub, 'five_inch')
  >>> IFiveClub.providedBy(club)
  True
  >>> isinstance(club, FiveInchClub)
  True

"""
from zope.interface import Interface, implements
from five.grokkers import grok

class IFiveClub(Interface):
    pass

class ITinyClub(Interface):
    pass

class FiveInchClub(grok.GlobalUtility):
    grok.implements(IFiveClub, ITinyClub)
    grok.provides(IFiveClub)
    grok.name('five_inch')
