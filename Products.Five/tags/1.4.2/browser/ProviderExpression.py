##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Provider tales expression registrations

$Id: tales.py 39606 2005-10-25 02:59:26Z srichter $
"""
__docformat__ = 'restructuredtext'
from Products.PageTemplates.Expressions import StringExpr
from Products.PageTemplates.Expressions import getEngine
from AccessControl.ZopeGuards import guarded_hasattr
from AccessControl.ZopeSecurityPolicy import getRoles
import Products.Five.security

import zope.component
import zope.schema
import zope.interface
from zope.contentprovider import interfaces
from zope.contentprovider.tales import addTALNamespaceData

_noroles = []

class ProviderExpr(StringExpr):
    """A provider expression for Zope2 templates.
    """

    zope.interface.implements(interfaces.ITALESProviderExpression)
    def __call__(self, econtext):
        name = StringExpr.__call__(self, econtext)
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # Try to look up the provider.
        provider = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IContentProvider, name)

        # Provide a useful error message, if the provider was not found.
        if provider is None:
            raise interfaces.ContentProviderLookupError(name)

        if getattr(provider, '__of__', None) is not None:
            provider = provider.__of__(context)

        # Insert the data gotten from the context
        addTALNamespaceData(provider, econtext)

        # Stage 1: Do the state update.
        provider.update()

        # Stage 2: Render the HTML content.
        return provider.render()

# Register Provider expression
getEngine().registerType('provider', ProviderExpr)
