from zope.interface import implements
from zope.app.container.btree import BTreeContainer

from interfaces import ICollector

class Collector(BTreeContainer):
    """A simple implementation of a collector using B-Tree
    Containers.

    Make sure that the ``Collector`` implements the ``ICollector``
    interface::

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(ICollector, Collector)
      True
  
    Here is an example of changing the description of the collector::

      >>> collector = Collector()
      >>> collector.description
      u''
      >>> collector.description = u'Ticket Collector Description'
      >>> collector.description
      u'Ticket Collector Description'
    """

    implements(ICollector)

    description = u''
