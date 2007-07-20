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
"""Browser code for JS calculator demo.

$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"
import os.path
import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from z3c.form import form, button, field
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent, jsfunction, interfaces

CalculatorCSSViewlet = CSSViewlet('calculator.css')

class IGridButton(interfaces.IJSButton):
    """A button within the grid."""

class CalculatorButton(jsaction.JSButton):
    zope.interface.implements(IGridButton)

    def __init__(self, *args, **kwargs):
        kwargs['accessKey'] = kwargs['title']
        super(CalculatorButton, self).__init__(*args, **kwargs)


class Literal(CalculatorButton):
    """Marker class for Literals."""
    pass

class Operator(CalculatorButton):
    """Marker class for operators."""
    pass

class IButtons(zope.interface.Interface):
    one = Literal(title=u'1')
    two = Literal(title=u'2')
    three = Literal(title=u'3')
    add = Operator(title=u'+')

    four = Literal(title=u'4')
    five = Literal(title=u'5')
    six = Literal(title=u'6')
    subtract = Operator(title=u'-')

    seven = Literal(title=u'7')
    eight = Literal(title=u'8')
    nine = Literal(title=u'9')
    multiply = Operator(title=u'*')

    zero = Literal(title=u'0')
    decimal = Literal(title=u'.')
    equal = Operator(title=u'=')
    divide = Operator(title=u'/')

    clear = jsaction.JSButton(title=u"C")


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


class CalculatorForm(layout.FormLayoutSupport, form.Form):
    zope.interface.implements(interfaces.IHaveJSFunctions)

    buttons = button.Buttons(IButtons)

    def updateActions(self):
        self.actions = GridButtonActions(self, self.request, self.context)
        self.actions.update()

    @jsfunction.function('calculator')
    def operate(self, id):
        return '''var operator = $("#operator .value").html();
                  var newOperator = $("#"+id).val();
                  var current = $("#current .value").html();
                  var stack = $("#stack .value").html();
                  if (operator == ""){
                      stack = current;
                      operator = newOperator;
                  } else if(newOperator == "="){
                      current = eval(stack+operator+current);
                      stack = "";
                      operator = "";
                  } else {
                      current = eval(stack+operator+current);
                      stack = current;
                  }

                  $("#operator .value").html(operator);
                  $("#stack .value").html(stack);
                  $("#recentOperator .value").html("True");
                  $("#current .value").html(current);'''

    @jsfunction.function('calculator')
    def addLiteral(self, id):
        return '''var recentOperator = $("#recentOperator .value").html();
                  var current = $("#current .value").html();
                  var number = $("#" + id).val();
                  if (recentOperator != ""){
                    current = "";
                  }
                  current = current+number;
                  $("#current .value").html(current);
                  $("#recentOperator .value").html("");
                  '''

    @jsfunction.function('calculator')
    def clear(self):
        return '''$("#stack .value").html("");
                  $("#current .value").html("");
                  $("#operator .value").html("");
                  $("#recentOperator .value").html("");'''

    @jsaction.handler(Operator)
    def handleOperator(self, event, selector):
        return 'calculator.operate("%s")' % selector.widget.id

    @jsaction.handler(Literal)
    def handleLiteral(self, event, selector):
        return 'calculator.addLiteral("%s")' % selector.widget.id

    @jsaction.handler(buttons['clear'])
    def handlerClear(self, event, selector):
        return 'calculator.clear()'
