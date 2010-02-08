from zope.interface import implements
from zope.container.btree import BTreeContainer

from tc.main.interfaces import ICollector

class Collector(BTreeContainer):
    """A simple implementation of a collector using B-Tree
    Container."""

    implements(ICollector)

    name = u""
    description = u""
