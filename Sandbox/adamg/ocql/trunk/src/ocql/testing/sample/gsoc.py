# -*- coding: UTF-8 -*-
from zope.interface import implements
from zope.app.container.btree import BTreeContainer

from ocql.testing.sample.interfaces import IGsoc

class Gsoc(BTreeContainer):
    """A simple implementation of the gsoc competetion using B-Tree Containers
    Make sure that the ‘‘Gsoc‘‘ implements the ‘‘IGsoc‘‘ interface:

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IGsoc, Gsoc)
    True

    Here is an example of changing the description of the gsoc object:
    >>> gsoc = Gsoc()
    >>> gsoc.description
    u''

    >>> gsoc.description = u'Gsoc Description'
    >>> gsoc.description
    u'Gsoc Description'
    """

    implements(IGsoc)

    description = u''
