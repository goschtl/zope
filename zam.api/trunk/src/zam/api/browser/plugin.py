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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
from zope.publisher.interfaces import NotFound
from zope.traversing.interfaces import IContainmentRoot
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.renderer import rest
from z3c.pagelet import browser
from z3c.form import button
from z3c.formui import form

from z3c.template.template import getPageTemplate

from zam.api import interfaces
from zam.api.i18n import MessageFactory as _


def render(text, request):
    return rest.ReStructuredTextToHTMLRenderer(text, request).render()


class PluginsPage(form.Form):
    """Plugin management page."""

    template = getPageTemplate()

    successMessage = _('Plugins status successfully changed.')
    NoChangesMessage = _('No plugin status get changed.')

    def plugins(self):
        for name, plugin in zope.component.getUtilitiesFor(interfaces.IPlugin):
            yield {
                'name': name,
                'title': plugin.title,
                'description': render(plugin.description, self.request),
                'isInstalled': plugin.isInstalled(self.context)
                }

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        changed = False
        for name, plugin in zope.component.getUtilitiesFor(interfaces.IPlugin):
            action = self.request.get(name)
            if action == 'uninstall' and plugin.isInstalled(self.context):
                plugin.uninstall(self.context)
                changed = True
            elif action == 'install' and not plugin.isInstalled(self.context):
                plugin.install(self.context)
                changed = True
        if changed:
            self.status = self.successMessage
        else:
            self.status = self.NoChangesMessage
