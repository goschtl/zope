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
"""ExtJS Component representation.

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form.interfaces import IForm, DISPLAY_MODE, HIDDEN_MODE
from z3c.form.interfaces import IPasswordWidget, IRadioWidget, IButtonAction
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import ITextWidget, ISelectWidget, ISingleCheckBoxWidget

from z3c.formext import interfaces
from z3c.formext.jsoncompat import jsonEncode

class Component(object):

    def _getConfig(self):
        return {}

    def getConfig(self, json=False):
        return jsonEncode(self._getConfig()) if json else self._getConfig()

class Field(Component):

    xtype = None

    def __init__(self, widget):
        self.widget = widget

    def _getConfig(self):
        config = dict(
            name = self.widget.name,
            fieldLabel = self.widget.label,
            id = self.widget.id,
            value = self.widget.value)
        if self.xtype:
            config['xtype'] = self.xtype
        if self.widget.title:
            config['title'] = self.widget.title
        if self.widget.mode == DISPLAY_MODE:
            config['disabled'] = True
        if self.widget.mode == HIDDEN_MODE:
            config['hidden'] = True
        return config


class TextField(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(ITextWidget)

    xtype = 'textfield'

    def _getConfig(self, json=False):
        config = super(TextField, self)._getConfig()
        if IPasswordWidget.providedBy(self.widget):
            config['inputType'] = 'password'
        return config


class TextArea(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(ITextAreaWidget)

    xtype = 'textarea'


class DateField(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(interfaces.IExtJSDateWidget)

    xtype = 'datefield'

class ComboBox(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(ISelectWidget)

    xtype = 'combo'
    def _getConfig(self, json=False):
        config = super(ComboBox, self)._getConfig()
        config['hiddenName'] = config['name']+':list'
        config['triggerAction'] = 'all'
        config['editable'] = False
        #XXX: commented out, not sure why this was here
        #del config['name']
        config['store'] = [(item['value'], item['content'])
                           for item in self.widget.items]
        return config

class CheckBox(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(ISingleCheckBoxWidget)

    xtype = 'checkbox'
    def _getConfig(self, json=False):
        config = super(CheckBox, self)._getConfig()
        checkbox = self.widget.items[0]
        config['checked'] = checkbox['checked']
        config['fieldLabel'] = checkbox['label']
        del config['value']
        return config

class RadioGroup(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IRadioWidget)

    def _getConfig(self, json=False):
        config = dict(
            fieldLabel = self.widget.label,
            id = self.widget.id,
            xtype = 'radiogroup',
            items = [dict(boxLabel=item['label'],
                          id='%s-%s' % (self.widget.id, index),
                          name=self.widget.name,
                          inputValue=item['value'],
                          checked=item['checked'])
                     for index, item in enumerate(self.widget.items)]
            )
        # we must pass in an items list even if there aren't any.  So
        # we will just pass in one item that is hidden.  This is most
        # certainly less than ideal.
        if not config['items']:
            config['items'].append(dict(hidden=True))
        if self.widget.title:
            config['title'] = self.widget.title
        return config

class Button(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IButtonAction)

    xtype = 'button'
    def _getConfig(self, json=False):
        config = super(Button, self)._getConfig()
        config['text'] = self.widget.value
        del config['value']
        del config['fieldLabel']
        return config


def getButtonsConfig(form, asDict=True):
    if not hasattr(form, 'actions'):
        form.updateActions()
    if not asDict:
        return [interfaces.IExtJSComponent(action).getConfig()
                for action in form.actions.values()]
    return dict([(name, interfaces.IExtJSComponent(action).getConfig())
                 for name, action in form.actions.items()])

def getWidgetsConfig(form, asDict=True):
    if not asDict:
        widgets = []
        for widget in form.widgets.values():
            factory = interfaces.IExtJSComponent
            if hasattr(widget, 'componentFactory'):
                factory = widget.componentFactory
            widgets.append(factory(widget).getConfig())
        return widgets
    widgets = {}
    for name, widget in form.widgets.items():
        factory = interfaces.IExtJSComponent
        if hasattr(widget, 'componentFactory'):
            factory = widget.componentFactory
        widgets[name] = factory(widget).getConfig()
    return widgets

class FormPanel(Component):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IForm)

    xtype = 'formpanel'

    def __init__(self, form):
        self.form = form

    def _getConfig(self, json=False):
        config = dict(
            xtype=self.xtype,
            id=self.form.id,
            submitURL=self.form.action)
        if self.form.label:
            config['title'] = self.form.label
        if not self.form.widgets:
            self.form.updateWidgets()
        items = getWidgetsConfig(self.form, asDict=False)
        if items:
            config['items'] = items

        buttons = getButtonsConfig(self.form, asDict=False)
        if buttons:
            config['buttons'] = buttons
        if hasattr(self.form, 'renderTo'):
            config['renderTo'] = self.form.renderTo

        return config


class ClientButton(Button):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(interfaces.IClientButtonAction)

    def _getConfig(self, json=False):
        config = super(ClientButton, self)._getConfig()
        config['handler'] = {}
        if self.widget.field.success:
            config['handler']['success'] = self.widget.field.success
        if self.widget.field.failure:
            config['handler']['failure'] = self.widget.field.failure
        return config

def getAjaxButtonsConfig(form, asDict=True):
    if not asDict:
        buttons = getButtonsConfig(form, asDict=False)
        if hasattr(form, 'ajaxRequestHandlers'):
            for name, handler in form.ajaxRequestHandlers.items():
                if name in form.actions:
                    index = form.actions.keys().index(name)
                    buttons[index]['url'] = '%s/@@ajax/%s' % (
                        absoluteURL(form, form.request), name)
        return buttons
    buttons = getButtonsConfig(form, asDict=True)
    if hasattr(form, 'ajaxRequestHandlers'):
        for name, handler in form.ajaxRequestHandlers.items():
            if name in form.actions:
                buttons[name]['url'] = '%s/@@ajax/%s' % (
                    absoluteURL(form, form.request), name)
    return buttons


class ExtFormPanel(FormPanel):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(interfaces.IExtJSForm)

    def _getConfig(self, json=False):
        config = super(ExtFormPanel, self)._getConfig()
        config['ajaxHandlers'] = {}
        if hasattr(self.form, 'ajaxRequestHandlers'):
            for name, handler in self.form.ajaxRequestHandlers.items():
                if name in self.form.actions:
                    index = self.form.actions.keys().index(name)
                    config['buttons'][index]['url'] = '%s/@@ajax/%s' % (
                        absoluteURL(self.form, self.form.request), name)
                    id = self.form.actions[name].id
                    config['ajaxHandlers'][id] = '%s/@@ajax/%s' % (
                        absoluteURL(self.form, self.form.request), name)
        if hasattr(self.form, 'ownerCt'):
            config['ownerCt'] = self.form.ownerCt
        return config

