##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""A 'PageTemplateFile' without security restrictions.

$Id$
"""
import AccessControl.Owned
from Acquisition import aq_inner, aq_acquire
from DocumentTemplate.DT_Util import TemplateDict
from Shared.DC.Scripts.Bindings import Bindings
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.Expressions import createTrustedZopeEngine
from zope.app.pagetemplate import viewpagetemplatefile

_engine = createTrustedZopeEngine()
def getEngine():
    return _engine

class ViewPageTemplateFile(Bindings, AccessControl.Owned.Owned,
                           viewpagetemplatefile.ViewPageTemplateFile):

    _default_bindings = {'name_subpath': 'traverse_subpath'}
    _Bindings_ns_class = TemplateDict

    def __init__(self, filename, _prefix=None, content_type=None):
        self.ZBindings_edit(self._default_bindings)
        _prefix = self.get_path_from_prefix(_prefix)
        super(ViewPageTemplateFile, self).__init__(
            filename, _prefix, content_type)

    def pt_getEngine(self):
        return getEngine()

    def pt_getContext(self, instance, request, **kw):
        namespace = super(ViewPageTemplateFile, self).pt_getContext(
            instance, request, **kw)
        bound_names = namespace['options'].pop('bound_names')
        namespace.update(bound_names)

        context = aq_inner(instance.context)
        try:
            root = aq_acquire(context, 'getPhysicalRoot')()
        except AttributeError:
            raise
            # we can't access the root, probably because 'context' is
            # something that doesn't support Acquisition.  You lose.
            root = None
        namespace.update({
            'context': context,            
            'here': context,
            'container': context,
            'root': root,
            'user': AccessControl.getSecurityManager().getUser(),
            'modules': SecureModuleImporter,
            })
        return namespace

    # this will be called by Bindings.__call__
    def _exec(self, bound_names, args, kw):
        kw['bound_names'] = bound_names
        return viewpagetemplatefile.ViewPageTemplateFile.__call__(
            self, *args, **kw)

# BBB 2006/05/01 -- to be removed after 12 months
import zope.deprecation
zope.deprecation.deprecated(
    "ZopeTwoPageTemplateFile",
    "ZopeTwoPageTemplate has been renamed to ViewPageTemplateFile. "
    "The old name will disappear in Zope 2.12")
ZopeTwoPageTemplateFile = ViewPageTemplateFile
