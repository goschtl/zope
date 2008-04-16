##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.component import hooks
from zope.traversing.interfaces import TraversalError
from zope.traversing.namespace import view
from zope.traversing.namespace import getResource

from z3c.resource import interfaces



class resource(view):
    """Traversal handler for ++resource++
    
    Placeless setup:

    >>> import zope.component
    >>> from zope.app.testing import placelesssetup, ztapi
    >>> placelesssetup.setUp()
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> from z3c.resource.adapter import getResource
    >>> from z3c.resource import testing
    >>> from z3c.resource.resource import Resource
    >>> zope.component.provideAdapter(AttributeAnnotations)

    Setup IResourceLocation and IResource adapters:

    >>> zope.component.provideAdapter(getResource)

    Now we create our resource traversable container:

    >>> from z3c.resource.testing import Content
    >>> from zope.publisher.browser import TestRequest
    >>> content = Content()
    >>> request = TestRequest

    Traverse the resource traversable container without a name:

    >>> traverser = resource(content, request)
    >>> isinstance(traverser.traverse(None, ''), Resource)
    True
    >>> traverser.traverse(None, '').__parent__ is content
    True
    >>> traverser.traverse(None, '').__name__ == u'++resource++'
    True

    Traverse an existing name:

    >>> foo = testing.TestResourceItem()
    >>> res = interfaces.IResource(content)
    >>> res[u'foo'] = foo
    >>> traverser.traverse(u'foo', '') == foo
    True

    Traverse a non IResourceTraversable access:

    >>> fake = object()
    >>> traverser = resource(fake, request)
    >>> try:
    ...     traverser.traverse('', None)
    ... except TraversalError, e:
    ...     e[0] is fake, e[1]
    (True, 'Parameter context: IResourceTraversable required.')

    Tear down::

    >>> placelesssetup.tearDown()

    """

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        # preconditions
        traversable = self.context

        if not interfaces.IResourceTraversable.providedBy(traversable):
            raise TraversalError(traversable, 
                'Parameter context: IResourceTraversable required.')

        # essentials
        resource = interfaces.IResource(traversable)

        if name:
            try:
                return resource[name]
            except KeyError, e:
                pass

            site = hooks.getSite()
            return getResource(site, name, self.request)

        else:
            return resource
