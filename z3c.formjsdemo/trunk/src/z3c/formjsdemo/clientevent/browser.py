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
"""Browser code for JS button demo.

$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"
import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from zope.event import notify
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IAttributes
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import INameChooser
from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout

from z3c.formjs import jsaction, jsevent, ajax, jsclientevent

import interfaces, article

class ArticleAddForm(layout.FormLayoutSupport, form.AddForm):

    template = ViewPageTemplateFile('addarticle.pt')
    label = "Add an article"
    fields = field.Fields(interfaces.IArticle)

    def articles(self):
        return filter(interfaces.IArticle.providedBy, self.context.values())

    def create(self, data):
        art = article.Article()
        art.title = data['title']
        art.subtitle = data['subtitle']
        art.body = data['body']
        return art

    def add(self, object):
        name = object.title.lower().replace(' ','')
        context = removeSecurityProxy(self.context)
        name = INameChooser(context).chooseName(name, object)
        context[name] = object
        self._name = name

    def nextURL(self):
        return absoluteURL(removeSecurityProxy(self.context)[self._name], self.request)


class IButtons(zope.interface.Interface):
    notify = jsaction.JSButton(title=u'Notify')

class EventForm(jsclientevent.ClientEventsForm,
                ajax.AJAXRequestHandler,
                layout.FormLayoutSupport,
                form.EditForm):

    fields = field.Fields(interfaces.IArticle)

    @jsclientevent.listener((interfaces.IArticle, IObjectModifiedEvent))
    def customEventListener(self, event):
        attributes = []
        for attr in filter(IAttributes.providedBy, event.descriptions):
            attributes += list(attr.attributes)
        return 'alert("The following fields have changed: %s");' % ','.join(attributes)
