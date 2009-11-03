"""
  >>> from five.grok.ftests.site.local_site import *
  >>> universe = getRootFolder()

  >>> universe._setObject("earth", World(id="earth"))
  'earth'
  >>> from zope.app.component import interfaces
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.ISite, universe.earth)
  True

  >>> from zope.app.component.site import setSite
  >>> setSite(universe.earth)

  >>> universe.earth.getSiteManager()
  <PersistentComponents ...>

  >>> from zope import component
  >>> manager = component.getUtility(IEnergyManager)
  >>> manager
  <EnergyManager at ...>
  >>> manager.aq_parent
  <World at ...>
  >>> verifyObject(IEnergyManager, manager)
  True

"""

from zope.interface import Interface
from five import grok


class IEnergyManager(Interface):

    def power_on():
        """Power up the world.
        """

    def power_off():
        """Shutdown the world.
        """


class EnergyManager(grok.LocalUtility):

    grok.implements(IEnergyManager)

    def power_on(self):
        print "Light On!"

    def power_off(self):
        print "Light Off!"


class World(grok.Model, grok.Site):

    grok.local_utility(EnergyManager, IEnergyManager)

