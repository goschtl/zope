##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Setting bases for local sites.

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component
import zope.schema
from zope.i18nmessageid import ZopeMessageFactory as _
from zope.app.component import vocabulary
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form

BASENAME = _('-- Global Base Registry --')

class BaseComponentsVocabulary(vocabulary.UtilityVocabulary):
    """A vocabulary for ``IComponents`` utilities."""

    interface = zope.component.interfaces.IComponents

    def __init__(self, context, **kw):
        super(BaseComponentsVocabulary, self).__init__(context, **kw)
        self._terms[BASENAME] = vocabulary.UtilityTerm(
            zope.component.globalregistry.base, BASENAME)

class IComponentsBases(zope.interface.Interface):
    """An interface describing the bases API of the IComponents object."""

    __bases__ = zope.schema.List(
        title=_('Bases'),
        description=_('The base components registires of this registry.'),
        value_type=zope.schema.Choice(vocabulary='Base Components'),
        required=True)


class SetBasesPage(form.EditForm):
    """A page to set the bases of a local site manager"""
    form_fields = form.FormFields(IComponentsBases)

