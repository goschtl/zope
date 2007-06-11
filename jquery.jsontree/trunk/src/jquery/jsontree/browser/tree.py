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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing import api
from zope.traversing.browser import absoluteURL
from zope.viewlet.interfaces import IViewlet
from zope.contentprovider.interfaces import IContentProvider
from zope.app.container.interfaces import IReadContainer
from zope.app.intid.interfaces import IIntIds
from z3c.template.template import getPageTemplate

from jquery.jsontree import interfaces
from jquery.jsontree.interfaces import JSON_TREE_ID
from jquery.jsontree import base


# simple trees
class SimpleJSONTree(base.TreeBase, base.PythonRendererMixin, 
    base.IdGeneratorMixin):
    """Simple JSON tree using inline methods for rendering elements and
    using traversable path for item lookup.
    """

    zope.interface.implements(interfaces.ISimpleJSONTree)

    def update(self):
        super(SimpleJSONTree, self).update()


# simple tree viewlet
class SimpleJSONTreeViewlet(SimpleJSONTree):
    """Simple JSON tree viewlet."""

    zope.interface.implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(SimpleJSONTreeViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager


# generic template based tree
class LITagProvider(base.ProviderBase, base.IdGeneratorMixin):
    """LI tag content provider."""

    zope.interface.implements(interfaces.ILITagProvider)
    zope.component.adapts(zope.interface.Interface, IBrowserRequest, 
        interfaces.ITemplateRenderer)

    jsonTreeId = JSON_TREE_ID


class ULTagProvider(base.ProviderBase, base.IdGeneratorMixin):
    """UL tag contet provider."""

    zope.interface.implements(interfaces.IULTagProvider)
    zope.component.adapts(zope.interface.Interface, IBrowserRequest, 
        interfaces.ITemplateRenderer)

    childTags = None

    jsonTreeId = JSON_TREE_ID


class TreeProvider(base.ProviderBase, base.IdGeneratorMixin):
    """UL tag contet provider."""

    zope.interface.implements(interfaces.ITreeProvider)
    zope.component.adapts(zope.interface.Interface, IBrowserRequest, 
        interfaces.ITemplateRenderer)

    # provider id, class and name
    jsonTreeId = JSON_TREE_ID
    jsonTreeClass = JSON_TREE_ID
    jsonTreeName = JSON_TREE_ID
    childTags = None


class GenericJSONTree(base.TreeBase, base.TemplateRendererMixin, 
    base.IdGeneratorMixin):
    """IntId base object lookup and template base rendering.
    
    This implementation uses IContentProvider for element tag rendering.
    This content provider are resonsible for represent a node. This allows us 
    to embed html or javascript calls in the html representation in a smart 
    way.
    """

    zope.interface.implements(interfaces.IGenericJSONTree)

    liProviderName = 'li'
    ulProviderName = 'ul'
    treeProviderName = 'tree'

    def update(self):
        super(GenericJSONTree, self).update()


# generic tree viewlet
class GenericJSONTreeViewlet(GenericJSONTree):
    """Generic JSON tree viewlet."""

    zope.interface.implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(GenericJSONTreeViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager
