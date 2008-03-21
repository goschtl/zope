##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" `browser:cssregistry` directive

$Id$
"""
from zope import interface
from z3ext.layout.pagelet import BrowserPagelet
from z3ext.statusmessage.interfaces import IStatusMessage

from z3ext.cssregistry.i18n import _
from z3ext.cssregistry.registry import registries
from z3ext.cssregistry.property import CSSProperty
from z3ext.cssregistry.interfaces import ICSSRegistry


class ViewRegistry(BrowserPagelet):

    def listRegistries(self):
        regs = []
        for key, registry in registries.items():
            name, layer = key

            regs.append({'name': name or 'Without name', 
                         'layer': '%s.%s'%(layer.__module__, layer.__name__),
                         'registry': registry})

        return regs

    def update(self):
        request = self.request

        if 'form.copy' in request:
            reg = request.get('registry', None)

            try:
                registry = self.listRegistries()[int(reg)]['registry']

                for prop, value in registry.items():
                    self.context[prop] = value

                IStatusMessage(request).add(
                    _(u"CSS Registry has been copied."))
            except:
                pass

        if 'form.add' in request:
            name = request.get('form.add.name', '').strip()
            if not name:
                IStatusMessage(request).add(
                    _(u"Can't add property with emtpy name."), 'error')
            else:
                self.context[name] = CSSProperty(
                    name, request.get('form.add.value', ''))

        if 'form.remove' in request:
            for prop in request.get('property', ()):
                del self.context[prop]
            IStatusMessage(request).add(_(u"Properties have been removed."))

        if 'form.save' in request:

            for key, value in request.form.items():
                if key.startswith('prop-'):
                    key = key[5:]
                    self.context[key].value = value

            if request.get('form.enabled') == 'yes':
                self.context.enabled = True
            else:
                self.context.enabled = False

            IStatusMessage(request).add(_(u"Properties have been changed."))

        return self.index()
