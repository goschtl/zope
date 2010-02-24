from zope.interface import implements
from zope.container.btree import BTreeContainer

from interfaces import ISampleApplication


class SampleApplication(BTreeContainer):

    implements(ISampleApplication)
    name = u""
    description = u""

