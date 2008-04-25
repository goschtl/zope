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
"""Calculator Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import decimal
import zope.interface
from zope.session.interfaces import ISession
from zope.viewlet.viewlet import CSSViewlet
from z3c.form import button, form, interfaces
from z3c.formui import layout

SESSION_KEY = 'z3c.formdemo.calculator'

CalculatorCSSViewlet = CSSViewlet('calculator.css')

class SessionProperty(object):

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, inst, klass):
        session = ISession(inst.request)[SESSION_KEY]
        return session.get(self.name, self.default)

    def __set__(self, inst, value):
        session = ISession(inst.request)[SESSION_KEY]
        session[self.name] = value


class IGridButton(interfaces.IButton):
    """A button within the grid."""


class Literal(button.Button):
    zope.interface.implements(IGridButton)

    def __init__(self, *args, **kwargs):
        literal = kwargs.pop('literal', None)
        super(Literal, self).__init__(*args, **kwargs)
        if literal is None:
            self.literal = self.title
        else:
            self.literal = literal
        self.accessKey = self.literal


class Operator(button.Button):
    zope.interface.implements(IGridButton)

    operation = None

    def __init__(self, *args, **kwargs):
        self.operation = kwargs.pop('operation', None)
        kwargs['accessKey'] = kwargs['title']
        super(Operator, self).__init__(*args, **kwargs)

    def operate(self, x, y):
        return getattr(x, self.operation)(y)


class GridButtonActions(button.ButtonActions):

    cols = 4

    def grid(self):
        rows = []
        current = []
        for button in self.values():
            if not IGridButton.providedBy(button.field):
                continue
            current.append(button)
            if len(current) == self.cols:
                rows.append(current)
                current = []
        if current:
            current += [None]*(self.cols-len(current))
            rows.append(current)
        return rows


class Calculator(layout.FormLayoutSupport, form.Form):

    buttons = button.Buttons(
        Literal('one', title=u'1'),
        Literal('two', title=u'2'),
        Literal('three', title=u'3'),
        Operator('add', title=u'+', operation='__add__'),

        Literal('four', title=u'4'),
        Literal('five', title=u'5'),
        Literal('six', title=u'6'),
        Operator('sub', title=u'-', operation='__sub__'),

        Literal('seven', title=u'7'),
        Literal('eight', title=u'8'),
        Literal('nine', title=u'9'),
        Operator('mul', title=u'*', operation='__mul__'),

        Literal('zero', title=u'0'),
        Literal('dec', title=u'.'),
        Operator('eq', title=u'='),
        Operator('div', title=u'/', operation='__div__'),

        button.Button('clear', title=u'C', accessKey=u"c"),
        )

    stack = SessionProperty('stack', decimal.Decimal(0))
    operator = SessionProperty('operator')
    current = SessionProperty('current', u'')

    maxSize = 12

    def updateActions(self):
        self.actions = GridButtonActions(self, self.request, self.context)
        self.actions.update()

    @button.handler(Literal)
    def handleLiteral(self, action):
        if len(self.current) < self.maxSize:
            self.current += action.field.literal
        if self.operator is None:
            self.stack = decimal.Decimal(0)

    @button.handler(Operator)
    def handleOperator(self, action):
        try:
            current = decimal.Decimal(self.current)
        except decimal.DecimalException:
            current = decimal.Decimal(0)
        if self.operator is not None:
            try:
                self.stack = self.operator.operate(self.stack, current)
            except decimal.DecimalException, err:
                self.current = u'-E-'
                return err
        else:
            self.stack = current
        self.current = u''
        self.operator = action.field

    @button.handler(buttons['eq'])
    def handleEqual(self, action):
        error = self.handleOperator(self, action)
        if not error:
            self.operator = None
            self.current = str(self.stack)

    @button.handler(buttons['clear'])
    def handleClear(self, action):
        self.operator = None
        self.stack = decimal.Decimal(0)
        self.current = u''
