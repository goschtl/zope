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
import zope.schema.interfaces
from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IForm, DISPLAY_MODE, HIDDEN_MODE
from z3c.form.interfaces import IGroup
from z3c.form.interfaces import IRadioWidget, IButtonAction
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import ITextWidget
from z3c.form.interfaces import ISelectWidget
from z3c.form.interfaces import ISingleCheckBoxWidget
from z3c.form.interfaces import IFormLayer

from z3c.formext import interfaces
from z3c.formext.jsoncompat import jsonEncode


class Component(object):

    def _getConfig(self):
        return {}

    def getConfig(self, json=False):
        if json:
            return jsonEncode(self._getConfig(), context=self.request)
        return self._getConfig()


class Field(Component):

    xtype = None

    def __init__(self, context, request, form, widget, field):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget
        self.field = field

    def _getConfig(self):
        config = dict(
            name = self.widget.name,
            fieldLabel = self.widget.label,
            id = self.widget.id,
            value = self.widget.value)
        if self.xtype:
            config['xtype'] = self.xtype
        title = self.widget.title
        if self.widget.title:
            config['title'] = self.widget.title
        if self.widget.mode == DISPLAY_MODE:
            config['disabled'] = True
        if self.widget.mode == HIDDEN_MODE:
            config['hidden'] = True
        if self.widget.required:
            config['itemCls'] = 'required'
        return config


class TextField(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextWidget,
            zope.schema.interfaces.IField)

    xtype = 'textfield'

    def _getConfig(self, json=False):
        config = super(TextField, self)._getConfig()
        config['allowBlank'] = not self.widget.required
        if zope.schema.interfaces.IMinMaxLen.providedBy(self.field):
            if self.field.min_length is not None:
                config['minLength'] = self.field.min_length
            if self.field.max_length is not None:
                config['maxLength'] = self.field.max_length
        if zope.schema.interfaces.IMinMax.providedBy(self.field):
            converter = IDataConverter(self.widget)
            if self.field.min is not None:
                config['minValue'] = converter.toWidgetValue(self.field.min)
            if self.field.max is not None:
                config['maxValue'] = converter.toWidgetValue(self.field.max)
        return config


class DateField(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextWidget,
            zope.schema.interfaces.IDate)

    xtype = 'datefield'


class TimeField(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextWidget,
            zope.schema.interfaces.ITime)

    xtype = 'timefield'

class NumberField(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextWidget,
            zope.schema.interfaces.IField)
    xtype = 'numberfield'

    def _getConfig(self, json=False):
        config = super(NumberField, self)._getConfig()
        config['allowDecimals'] = \
                not zope.schema.interfaces.IInt.providedBy(self.field)
        return config


class Password(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextWidget,
            zope.schema.interfaces.IPassword)

    def _getConfig(self, json=False):
        config = super(Password, self)._getConfig()
        config['inputType'] = 'password'
        return config


class TextArea(TextField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ITextAreaWidget,
            zope.schema.interfaces.IField)

    xtype = 'textarea'


class DateWidget(DateField):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            interfaces.IExtJSDateWidget,
            zope.schema.interfaces.IDate)


class ComboBox(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ISelectWidget,
            zope.schema.interfaces.IChoice)

    xtype = 'combo'

    def _getConfig(self, json=False):
        config = super(ComboBox, self)._getConfig()
        config.update(dict(
            hiddenName = config['name']+':list',
            triggerAction = 'all',
            editable = False,
            store= [(item['value'], item['content'])
                for item in self.widget.items],
            ))
        return config


class CheckBox(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            ISingleCheckBoxWidget,
            zope.schema.interfaces.IField)

    xtype = 'checkbox'

    def _getConfig(self, json=False):
        config = super(CheckBox, self)._getConfig()
        checkbox = self.widget.items[0]
        config.update(dict(
            checked = checkbox['checked'],
            fieldLabel = checkbox['label'],
            ))
        del config['value']
        return config


class RadioGroup(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(
            zope.interface.Interface,
            IFormLayer,
            IForm,
            IRadioWidget,
            zope.schema.interfaces.IField)

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
                     for index, item in enumerate(self.widget.items)],
            )
        # we must pass in an items list even if there aren't any.  So
        # we will just pass in one item that is hidden.  This is most
        # certainly less than ideal.
        if not config['items']:
            config['items'].append(dict(hidden=True))
        if self.widget.title:
            config['title'] = self.widget.title
        return config


@zope.component.adapter(IWidget)
@zope.interface.implementer(interfaces.IExtJSComponent)
def SimpleFiedWidgetFactory(widget):
    return zope.component.getMultiAdapter(
            (widget.context, widget.request, widget.form,
            widget, widget.field),
            interfaces.IExtJSComponent)


class Button(Field):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IButtonAction)

    xtype = 'button'

    def __init__(self, widget):
        super(Button, self).__init__(None, None, None, widget, None)

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


def getWidgetConfig(widget):
    """Get the wiget as a json serializable object
    """
    component = None
    #first try to get the componentFactory from the widget
    factory = getattr(widget, 'componentFactory', None)
    if factory is not None:
        component = factory(widget.context, widget.request,
                widget.form, widget, widget.field)
    #if not provided try to get one from the registry
    if component is None:
        component = zope.component.queryMultiAdapter(
            (widget.context, widget.request,
                widget.form, widget, widget.field),
            interfaces.IExtJSComponent)
    #fallback to a simple adapter
    if component is None:
        component = interfaces.IExtJSComponent(widget)
    return component.getConfig()


def getWidgetsConfig(form, asDict=True):
    if not asDict:
        widgets = []
        for widget in form.widgets.values():
            config = getWidgetConfig(widget)
            widgets.append(config)
        return widgets
    widgets = {}
    for name, widget in form.widgets.items():
        config = getWidgetConfig(widget)
        widgets[name] = config
    return widgets


def getGroupsConfig(form, json=False):
    items = []
    if form.groups:
        for group in form.groups:
            groupComponent = interfaces.IExtJSComponent(group)
            groupConfig = groupComponent._getConfig(json)
            items.append(groupConfig)
    return items


class Panel(Component):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IForm)

    xtype = 'panel'

    def __init__(self, form):
        self.form = form

    def _getConfig(self, json=False):
        config = dict(
            xtype=self.xtype)
        if self.form.label:
            config['title'] = self.form.label
        if not self.form.widgets:
            self.form.updateWidgets()
        items = getWidgetsConfig(self.form, asDict=False)
        if items:
            config['items'] = items
        if hasattr(self.form, 'renderTo'):
            config['renderTo'] = self.form.renderTo
        #update config
        cfg = zope.component.queryMultiAdapter(
                (self.form.context, self.form.request, self.form),
                interfaces.IExtJSConfigValue)
        if cfg:
            config.update(cfg.get())
        return config


class GroupPanel(Panel):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(IGroup)

    def _getConfig(self, json=False):
        config = super(GroupPanel, self)._getConfig(json)
        items = config.get("items", [])
        items += getGroupsConfig(self.form, json)
        config['items'] = items
        return config


class FormPanel(Panel):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(interfaces.IBaseForm)

    xtype = 'formpanel'

    def _getConfig(self, json=False):
        config = super(FormPanel, self)._getConfig(json)
        config['id'] = self.form.id
        config['submitURL'] = self.form.action
        buttons = getButtonsConfig(self.form, asDict=False)
        if buttons:
            config['buttons'] = buttons
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


class ExtGroupFormPanel(ExtFormPanel):
    zope.interface.implements(interfaces.IExtJSComponent)
    zope.component.adapts(interfaces.IExtJSGroupForm)

    def _getConfig(self, json=False):
        config = super(ExtGroupFormPanel, self)._getConfig()
        items = config.get("items", [])
        items += getGroupsConfig(self.form, json)
        config['items'] = items
        return config
